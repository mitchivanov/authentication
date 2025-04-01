import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional

class UserRegisterSchema(BaseModel):
    """
    Схема для регистрации нового пользователя.
    
    Определяет поля и правила валидации для данных, 
    необходимых при регистрации пользователя.
    """
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        pattern=r'^[a-zA-Z0-9_-]+$', 
        description="Имя пользователя (3-20 символов, только буквы, цифры, подчеркивания и дефисы)"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=20,
        description="Пароль (8-20 символов, минимум одна заглавная буква, одна строчная буква, одна цифра и один спецсимвол)"
    )
    email: EmailStr = Field(..., description="Электронная почта")
    date_of_birth: date = Field(..., description="Дата рождения в формате ISO (YYYY-MM-DD)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user123",
                    "password": "SecurePass1!",
                    "email": "user@example.com",
                    "date_of_birth": "1990-01-01"
                }
            ]
        }
    }
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(c in '@$!%*?&#' for c in v):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол (@$!%*?&#)")
        return v
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        if v < date(1900, 1, 1):
            raise ValueError("Дата рождения не может быть ранее 1900-01-01")
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Некорректный формат email")
        return v

class UserInfoSchema(BaseModel):
    """
    Схема для информации о пользователе.
    
    Определяет поля, которые возвращаются при запросе
    информации о пользователе.
    """
    username: str
    email: str
    date_of_birth: Optional[date] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user123",
                    "email": "user@example.com",
                    "date_of_birth": "1990-01-01"
                }
            ]
        }
    }

class UserUpdateSchema(BaseModel):
    """
    Схема для обновления информации о пользователе.
    
    Определяет поля, которые могут быть обновлены у пользователя.
    Все поля опциональны.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        None, 
        min_length=8, 
        max_length=20,
        description="Новый пароль (8-20 символов, минимум одна заглавная буква, одна строчная буква, одна цифра и один спецсимвол)"
    )
    date_of_birth: Optional[date] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "new_email@example.com",
                    "password": "NewSecurePass1!",
                    "date_of_birth": "1990-01-01"
                }
            ]
        }
    }
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
            
        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(c in '@$!%*?&#' for c in v):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол (@$!%*?&#)")
        return v
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
            
        if v > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        if v < date(1900, 1, 1):
            raise ValueError("Дата рождения не может быть ранее 1900-01-01")
        return v 