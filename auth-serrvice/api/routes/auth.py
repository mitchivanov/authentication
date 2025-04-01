from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from application.services.auth_service import AuthApplicationService
from domain.schemas.auth import LoginSchema, TokenSchema, RefreshTokenSchema, LogoutSchema
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.config.database import get_session
from infrastructure.middleware.auth import get_current_user
from infrastructure.dependencies.services import get_auth_service

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Неавторизованный доступ"}}
)

# Функция для получения сервиса аутентификации
async def get_auth_service(session: AsyncSession = Depends(get_session)):
    repository = UserRepository(session)
    return AuthApplicationService(repository)

@router.post("/login", response_model=TokenSchema)
async def login(
    login_data: LoginSchema,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Аутентификация пользователя и выдача JWT-токенов.
    
    Аутентифицирует пользователя по имени и паролю и возвращает токены доступа и обновления.
    """
    tokens = await auth_service.authenticate_user(login_data.username, login_data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens

@router.post("/login/oauth", response_model=TokenSchema)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Аутентификация пользователя через форму OAuth2.
    
    Эндпоинт для совместимости с OAuth2 клиентами. Аутентифицирует пользователя
    по имени и паролю с использованием стандартной формы OAuth2 и возвращает токены.
    """
    tokens = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenSchema(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    refresh_data: RefreshTokenSchema,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Обновление токена доступа.
    
    Использует действующий токен обновления для выдачи нового токена доступа.
    """
    try:
        new_tokens = await auth_service.refresh_token(refresh_data.refresh_token)
        return new_tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    logout_data: LogoutSchema,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Выход из системы.
    
    Аннулирует токен обновления, делая его недействительным для последующих запросов.
    """
    await auth_service.logout(logout_data.refresh_token)
    return None

@router.get("/oauth/{provider}")
async def oauth_login(
    provider: str,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """
    Авторизация через OAuth2 провайдера.
    
    Инициирует процесс авторизации через внешнего OAuth2 провайдера (Google, Facebook, GitHub и т.д.).
    Перенаправляет пользователя на страницу авторизации провайдера.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Авторизация через {provider} в настоящее время не реализована"
    ) 