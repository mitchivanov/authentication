from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

# Обобщенный тип для сущностей
T = TypeVar('T')

class RepositoryInterface(Generic[T], ABC):
    """
    Базовый интерфейс для всех репозиториев.
    
    Определяет общие методы, которые должны быть реализованы
    всеми конкретными репозиториями.
    """
    
    @abstractmethod
    async def get_by_id(self, id_value: any) -> Optional[T]:
        """
        Получить сущность по ID.
        
        Args:
            id_value: Значение первичного ключа
            
        Returns:
            Optional[T]: Найденная сущность или None
        """
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        """
        Получить список всех сущностей.
        
        Returns:
            List[T]: Список сущностей
        """
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Создать новую сущность.
        
        Args:
            entity: Сущность для создания
            
        Returns:
            T: Созданная сущность
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Обновить существующую сущность.
        
        Args:
            entity: Сущность с обновленными данными
            
        Returns:
            T: Обновленная сущность
        """
        pass
    
    @abstractmethod
    async def delete(self, id_value: any) -> bool:
        """
        Удалить сущность по ID.
        
        Args:
            id_value: Значение первичного ключа
            
        Returns:
            bool: True если сущность была удалена, иначе False
        """
        pass

class UserRepositoryInterface(RepositoryInterface[T], ABC):
    """
    Интерфейс для репозитория пользователей.
    
    Определяет специфичные для пользователей методы в дополнение
    к общим методам из базового интерфейса.
    """
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[T]:
        """
        Получить пользователя по имени пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Optional[T]: Найденный пользователь или None
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[T]:
        """
        Получить пользователя по email.
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[T]: Найденный пользователь или None
        """
        pass 