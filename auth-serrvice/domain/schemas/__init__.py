"""
Схемы домена для валидации данных.

Этот модуль содержит схемы Pydantic для валидации входных и выходных данных API.
Эти схемы определяют структуру данных и правила валидации на уровне домена.
"""

# Импортируем схемы пользователя
from .user import (
    UserRegisterSchema, 
    UserInfoSchema, 
    UserUpdateSchema
)

# Импортируем схемы аутентификации
from .auth import (
    TokenSchema, 
    LoginSchema, 
    RefreshTokenSchema, 
    LogoutSchema, 
    TokenPayloadSchema
)

__all__ = [
    # Схемы пользователя
    "UserRegisterSchema", 
    "UserInfoSchema", 
    "UserUpdateSchema",
    
    # Схемы аутентификации
    "TokenSchema", 
    "LoginSchema", 
    "RefreshTokenSchema", 
    "LogoutSchema", 
    "TokenPayloadSchema"
]
