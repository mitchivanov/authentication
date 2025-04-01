from pydantic import BaseModel, Field
from typing import Optional, List

class TokenSchema(BaseModel):
    """
    Схема для JWT токенов.
    
    Определяет структуру ответа при успешной аутентификации,
    включая токены доступа и обновления.
    """
    access_token: str = Field(..., description="Токен доступа JWT")
    refresh_token: str = Field(..., description="Токен обновления JWT")
    token_type: str = Field(default="bearer", description="Тип токена")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    }

class LoginSchema(BaseModel):
    """
    Схема для логина пользователя.
    
    Определяет данные, необходимые для аутентификации пользователя.
    """
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль пользователя")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user123",
                    "password": "SecurePass1!"
                }
            ]
        }
    }

class RefreshTokenSchema(BaseModel):
    """
    Схема для обновления токена.
    
    Определяет данные, необходимые для обновления токена доступа.
    """
    refresh_token: str = Field(..., description="Действующий токен обновления JWT")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            ]
        }
    }

class LogoutSchema(BaseModel):
    """
    Схема для выхода из системы.
    
    Определяет данные, необходимые для выхода из системы
    и аннулирования токенов.
    """
    refresh_token: str = Field(..., description="Токен обновления для аннулирования")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            ]
        }
    }

class TokenPayloadSchema(BaseModel):
    """
    Схема для полезной нагрузки JWT-токена.
    
    Определяет структуру данных, хранящихся в JWT-токене.
    """
    sub: str = Field(..., description="Идентификатор субъекта (username)")
    permissions: Optional[List[str]] = Field(default=None, description="Список разрешений пользователя")
    exp: Optional[int] = Field(default=None, description="Время истечения срока действия токена (в секундах с эпохи Unix)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sub": "user123",
                    "permissions": ["read:users", "write:users"],
                    "exp": 1625097600
                }
            ]
        }
    } 