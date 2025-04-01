"""
Маршруты API.

Этот модуль обеспечивает единую точку доступа ко всем маршрутам API.
"""
from fastapi import APIRouter

# Создаем маршрутизатор для API
router = APIRouter()

# Импортируем и подключаем все маршруты
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router

# Подключаем все маршрутизаторы
router.include_router(auth_router)
router.include_router(users_router)

# Экспортируем router для импорта из других модулей
__all__ = ["router"] 