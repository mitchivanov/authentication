from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.database import get_session
from infrastructure.repositories.user_repository import UserRepository
from application.services.auth_service import AuthApplicationService
from application.services.user_service import UserApplicationService

async def get_user_repository(session: AsyncSession = Depends(get_session)):
    """
    Зависимость для получения репозитория пользователей.
    
    Args:
        session: Асинхронная сессия базы данных
        
    Returns:
        UserRepository: Репозиторий пользователей
    """
    return UserRepository(session)

async def get_auth_service(user_repository = Depends(get_user_repository)):
    """
    Зависимость для получения сервиса аутентификации.
    
    Args:
        user_repository: Репозиторий пользователей
        
    Returns:
        AuthApplicationService: Сервис аутентификации
    """
    return AuthApplicationService(user_repository)

async def get_user_service(user_repository = Depends(get_user_repository)):
    """
    Зависимость для получения сервиса пользователей.
    
    Args:
        user_repository: Репозиторий пользователей
        
    Returns:
        UserApplicationService: Сервис пользователей
    """
    return UserApplicationService(user_repository) 