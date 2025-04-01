from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import date

from domain.entities.user import User

class UserServiceInterface(ABC):
    """
    Интерфейс для сервисов, работающих с пользователями.
    
    Определяет методы для управления пользователями,
    которые должны быть реализованы в конкретных сервисах.
    """
    
    @abstractmethod
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Получить информацию о пользователе.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Dict[str, Any]: Информация о пользователе
        """
        pass
    
    @abstractmethod
    async def register_user(self, username: str, email: str, password: str, 
                           date_of_birth: date) -> User:
        """
        Зарегистрировать нового пользователя.
        
        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль пользователя
            date_of_birth: Дата рождения
            
        Returns:
            User: Созданный пользователь
        """
        pass
    
    @abstractmethod
    async def update_user(self, username: str, **kwargs) -> User:
        """
        Обновить информацию о пользователе.
        
        Args:
            username: Имя пользователя
            **kwargs: Поля для обновления
            
        Returns:
            User: Обновленный пользователь
        """
        pass
    
    @abstractmethod
    async def delete_user(self, username: str) -> Dict[str, str]:
        """
        Удалить пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Dict[str, str]: Сообщение об успешном удалении
        """
        pass

class AuthServiceInterface(ABC):
    """
    Интерфейс для сервисов аутентификации.
    
    Определяет методы для аутентификации и авторизации пользователей.
    """
    
    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Dict[str, str]:
        """
        Аутентифицировать пользователя.
        
        Args:
            username: Имя пользователя
            password: Пароль пользователя
            
        Returns:
            Dict[str, str]: Токены аутентификации
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Обновить токен доступа.
        
        Args:
            refresh_token: Токен обновления
            
        Returns:
            Dict[str, str]: Новые токены
        """
        pass
    
    @abstractmethod
    async def logout(self, username: str) -> Dict[str, str]:
        """
        Выход пользователя из системы.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Dict[str, str]: Сообщение об успешном выходе
        """
        pass
    
    @abstractmethod
    def verify_csrf_token(self, cookie_token: str, header_token: str) -> bool:
        """
        Проверить CSRF токен.
        
        Args:
            cookie_token: Токен из куки
            header_token: Токен из заголовка
            
        Returns:
            bool: True если токены совпадают, иначе False
        """
        pass 