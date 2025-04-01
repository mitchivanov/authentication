import logging.config
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

# Импортируем роутеры из API
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from infrastructure.config.database import init_db
from infrastructure.middleware.rate_limit import setup_rate_limiter
from infrastructure.middleware.auth import csrf_protect
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from prometheus_fastapi_instrumentator import Instrumentator
from infrastructure.config.settings import settings, ALLOWED_ORIGINS

# Конфигурация логгирования с ротацией
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
            "propagate": True,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="Authentication Service",
    description="API for authentication and authorization",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Настройка Swagger UI для авторизации
app.swagger_ui_parameters = {
    "persistAuthorization": True,
    "defaultModelsExpandDepth": -1,
    "displayRequestDuration": True,
    "tryItOutEnabled": True,
}

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

# Добавление CSRF защиты
app.middleware("http")(csrf_protect)

# Настройка ограничения скорости запросов
limiter = setup_rate_limiter(app)

# Подключение маршрутов API
app.include_router(auth_router)
app.include_router(users_router)

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"message": f"Error: {exc.detail}"})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"General Exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error, please contact administrator"})

# События запуска и остановки
@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    # Инициализация Redis для кэширования
    try:
        # Создаем Redis соединение
        redis = aioredis.from_url(
            settings.REDIS_URL, 
            encoding="utf8", 
            decode_responses=True
        )
        # Инициализируем кэш
        FastAPICache.init(
            RedisBackend(redis), 
            prefix="fastapi-cache",
            expire=60  # Время жизни кэша по умолчанию в секундах
        )
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.warning(f"Could not initialize Redis cache: {e}")
        logger.warning("Continuing without Redis cache")

# Настройка метрик Prometheus
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)

# Простой тестовый маршрут
@app.get("/api/ping")
async def ping():
    """Simple ping endpoint to check if service is alive."""
    return {"status": "ok", "message": "Service is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == "development", workers=4) 