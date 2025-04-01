import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Загружаем переменные окружения из .env файла
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:paparoach228@localhost/abracadabra")
    
    # JWT настройки
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c87f29b2929ca004170af3400c48f53514f00961f201d")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # CSRF настройки
    CSRF_SECRET: str = os.getenv("CSRF_SECRET", "a3f1c2d4e5b67890abcdef1234567890abcdef1234567890abcdef1234567890")
    
    # CORS настройки
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"] if ENVIRONMENT == "development" else ["https://yourdomain.com"]
    SECURE_COOKIE: bool = ENVIRONMENT == "production"
    
    # Google OAuth2 настройки
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URI: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    REDIRECT_URI: str = "http://localhost:8000/api/login/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Redis настройки
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

# Создаем экземпляр настроек
settings = Settings()

# Экспортируем настройки
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
CSRF_SECRET = settings.CSRF_SECRET
ENVIRONMENT = settings.ENVIRONMENT
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
SECURE_COOKIE = settings.SECURE_COOKIE
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_AUTH_URI = settings.GOOGLE_AUTH_URI
GOOGLE_TOKEN_URI = settings.GOOGLE_TOKEN_URI
GOOGLE_USERINFO_URI = settings.GOOGLE_USERINFO_URI
REDIRECT_URI = settings.REDIRECT_URI
FRONTEND_URL = settings.FRONTEND_URL
REDIS_URL = settings.REDIS_URL 