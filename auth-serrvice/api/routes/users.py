from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from datetime import date

from domain.schemas.user import UserRegisterSchema, UserInfoSchema, UserUpdateSchema
from application.services.user_service import UserApplicationService
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.config.database import get_session
from infrastructure.middleware.auth import get_current_user
from infrastructure.dependencies.services import get_user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"description": "Неавторизованный доступ"}}
)

# Используем функцию из dependencies.services
# async def get_user_service(session: AsyncSession = Depends(get_session)):
#     repository = UserRepository(session)
#     return UserApplicationService(repository)

@router.post(
    "/register", 
    response_model=UserInfoSchema, 
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegisterSchema,
    user_service: UserApplicationService = Depends(get_user_service)
):
    """
    Регистрация нового пользователя.
    
    Создает нового пользователя с указанными данными.
    """
    user = await user_service.register_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        date_of_birth=user_data.date_of_birth
    )
    return user

@router.get("/me", response_model=UserInfoSchema)
async def get_current_user_info(
    current_username: str = Depends(get_current_user),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """
    Получение информации о текущем авторизованном пользователе.
    
    Возвращает данные текущего пользователя на основе JWT токена.
    """
    user = await user_service.get_user_by_username(current_username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.get(
    "/{username}", 
    response_model=UserInfoSchema,
    summary="Получение информации о пользователе",
    description="Возвращает информацию о пользователе по имени пользователя"
)
async def get_user_info(
    username: str,
    current_username: str = Depends(get_current_user),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """
    Получение информации о пользователе.
    
    - **username**: имя пользователя
    
    Требует авторизации через JWT-токен.
    Обычные пользователи могут получать информацию только о себе.
    """
    # Проверка, что пользователь запрашивает информацию о себе
    # TODO: добавить проверку на роли (админ может видеть всех пользователей)
    if username != current_username:
        user_info = await user_service.get_user_info(current_username)
    else:
        user_info = await user_service.get_user_info(username)
    
    return UserInfoSchema(**user_info)

@router.put("/me", response_model=UserInfoSchema)
async def update_current_user(
    user_data: UserUpdateSchema,
    current_username: str = Depends(get_current_user),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """
    Обновление информации о текущем пользователе.
    
    Обновляет данные текущего авторизованного пользователя.
    """
    updated_user = await user_service.update_user(
        username=current_username,
        email=user_data.email,
        password=user_data.password,
        date_of_birth=user_data.date_of_birth
    )
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_username: str = Depends(get_current_user),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """
    Удаление текущего пользователя.
    
    Удаляет учетную запись текущего авторизованного пользователя.
    """
    await user_service.delete_user(current_username)
    return None 