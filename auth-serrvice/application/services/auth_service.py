from fastapi import HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Optional, Tuple, Union
from datetime import datetime

from domain.entities.user import User
from domain.services.auth_service import AuthDomainService
from domain.schemas.auth import TokenSchema
from domain.interfaces.repositories import UserRepositoryInterface
from infrastructure.utils.security import verify_password, create_tokens, generate_csrf_token
from infrastructure.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, SECURE_COOKIE

class AuthApplicationService:
    """
    Сервис приложения для аутентификации и авторизации.
    
    Реализует сценарии использования, связанные с аутентификацией,
    такие как вход в систему, выход, обновление токенов и т.д.
    """
    
    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Инициализировать сервис с репозиторием пользователей.
        
        Args:
            user_repository: Репозиторий для работы с пользователями
        """
        self.user_repository = user_repository
        self.domain_service = AuthDomainService()
    
    async def login(
        self, 
        form_data: OAuth2PasswordRequestForm, 
        response: Response
    ) -> Dict[str, str]:
        """
        Авторизовать пользователя и выдать токены.
        
        Args:
            form_data: Данные формы авторизации
            response: Объект ответа для установки cookies
            
        Returns:
            Dict[str, str]: Токены доступа и обновления
            
        Raises:
            HTTPException: Если авторизация не удалась
        """
        user = await self.authenticate_user(form_data.username, form_data.password)
        
        # Создаем токены доступа и обновления
        access_token, refresh_token = await create_tokens({"sub": user.username})
        
        # Создаем CSRF токен
        csrf_token = generate_csrf_token()
        
        # Устанавливаем cookie для токенов
        self._set_auth_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "csrf_token": csrf_token
        }
    
    async def authenticate_user(self, username: str, password: str) -> Union[TokenSchema, None]:
        """
        Аутентифицировать пользователя по имени и паролю и создать токены.
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            TokenSchema: Токены доступа и обновления или None, если аутентификация не удалась
        """
        try:
            user = await self.user_repository.get_by_username(username)
            
            if not user:
                return None
            
            if not await verify_password(password, user.password_hash):
                return None
            
            # Создаем токены доступа и обновления
            access_token, refresh_token = await create_tokens({"sub": user.username})
            
            return TokenSchema(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        except Exception:
            return None
    
    async def refresh_token(self, refresh_token: str) -> TokenSchema:
        """
        Обновить токены доступа по refresh токену.
        
        Args:
            refresh_token: Токен обновления
            
        Returns:
            TokenSchema: Новые токены
            
        Raises:
            ValueError: Если обновление не удалось
        """
        try:
            from jose import jwt
            from infrastructure.config.settings import SECRET_KEY, ALGORITHM
            
            # Декодируем refresh токен
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            token_type = payload.get("type")
            exp = payload.get("exp")
            
            # Проверяем, что это refresh токен и он не истек
            if token_type != "refresh" or not username:
                raise ValueError("Недействительный refresh токен")
            
            # Проверяем, не истек ли токен
            expiry = datetime.fromtimestamp(exp)
            if self.domain_service.is_token_expired(expiry):
                raise ValueError("Истекший refresh токен")
            
            # Проверяем, существует ли пользователь
            user = await self.user_repository.get_by_username(username)
            if not user:
                raise ValueError("Пользователь не найден")
            
            # Создаем новые токены
            new_access_token, new_refresh_token = await create_tokens({"sub": username})
            
            return TokenSchema(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except Exception as e:
            raise ValueError(f"Не удалось обновить токен: {str(e)}")
    
    async def refresh(self, refresh_token: str, response: Response) -> Dict[str, str]:
        """
        Обновить токены доступа по refresh токену и установить cookies.
        
        Args:
            refresh_token: Токен обновления
            response: Объект ответа для установки cookies
            
        Returns:
            Dict[str, str]: Новые токены
            
        Raises:
            HTTPException: Если обновление не удалось
        """
        try:
            tokens = await self.refresh_token(refresh_token)
            
            # Создаем новый CSRF токен
            csrf_token = generate_csrf_token()
            
            # Устанавливаем cookie для новых токенов
            self._set_auth_cookies(
                response=response,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                csrf_token=csrf_token
            )
            
            return {
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "token_type": "bearer",
                "csrf_token": csrf_token
            }
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def logout(self, refresh_token: str = None, response: Response = None) -> Dict[str, str]:
        """
        Выйти из системы (аннулировать токены).
        
        Args:
            refresh_token: Токен обновления для аннулирования 
            response: Объект ответа для удаления cookies
            
        Returns:
            Dict[str, str]: Сообщение об успешном выходе
        """
        # Если передан refresh token, добавляем его в черный список
        if refresh_token:
            # TODO: Добавить токен в черный список, когда будет реализовано хранилище
            pass
            
        # Если передан объект ответа, удаляем cookies
        if response:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            response.delete_cookie("csrf_token")
        
        return {"message": "Вы успешно вышли из системы"}
    
    def verify_csrf_token(self, cookie_token: str, header_token: str) -> bool:
        """
        Проверить CSRF токен.
        
        Args:
            cookie_token: Токен из куки
            header_token: Токен из заголовка
            
        Returns:
            bool: True если токены совпадают, иначе False
        """
        return self.domain_service.verify_csrf_token(cookie_token, header_token)
    
    def _set_auth_cookies(
        self, 
        response: Response, 
        access_token: str, 
        refresh_token: str, 
        csrf_token: str
    ) -> None:
        """
        Установить куки для аутентификации.
        
        Args:
            response: Объект ответа
            access_token: Токен доступа
            refresh_token: Токен обновления
            csrf_token: CSRF токен
        """
        # Устанавливаем secure и httponly флаги в зависимости от окружения
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=SECURE_COOKIE,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=SECURE_COOKIE,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # Должен быть доступен из JavaScript
            secure=SECURE_COOKIE,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ) 