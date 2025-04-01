from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from domain.entities.user import User
from domain.interfaces.repositories import UserRepositoryInterface
from infrastructure.database.models.user_model import UserModel

class UserRepository(UserRepositoryInterface[User]):
    """
    Репозиторий для работы с пользователями в БД.
    
    Реализует интерфейс UserRepositoryInterface и предоставляет
    конкретные методы для работы с таблицей пользователей в БД.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализировать репозиторий с сессией БД.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session
    
    async def get_by_id(self, id_value: str) -> Optional[User]:
        """
        Получить пользователя по ID (имени пользователя).
        
        Args:
            id_value: Имя пользователя
            
        Returns:
            Optional[User]: Найденный пользователь или None
        """
        return await self.get_by_username(id_value)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по имени пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Optional[User]: Найденный пользователь или None
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return user_model.to_entity()
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email.
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Найденный пользователь или None
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return user_model.to_entity()
        return None
    
    async def list_all(self) -> List[User]:
        """
        Получить список всех пользователей.
        
        Returns:
            List[User]: Список пользователей
        """
        result = await self.session.execute(select(UserModel))
        user_models = result.scalars().all()
        return [user_model.to_entity() for user_model in user_models]
    
    async def create(self, entity: User) -> User:
        """
        Создать нового пользователя.
        
        Args:
            entity: Доменная сущность пользователя
            
        Returns:
            User: Созданный пользователь
        """
        user_model = UserModel.from_entity(entity)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        return user_model.to_entity()
    
    async def update(self, entity: User) -> User:
        """
        Обновить существующего пользователя.
        
        Args:
            entity: Доменная сущность пользователя с обновленными данными
            
        Returns:
            User: Обновленный пользователь
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == entity.username)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise ValueError(f"Пользователь с именем {entity.username} не найден")
        
        # Обновляем поля модели
        user_model.email = entity.email
        user_model.password_hashed = entity.password_hash
        user_model.date_of_birth = entity.date_of_birth
        user_model.bank_balance = entity.bank_balance
        
        await self.session.commit()
        await self.session.refresh(user_model)
        return user_model.to_entity()
    
    async def delete(self, id_value: str) -> bool:
        """
        Удалить пользователя по ID (имени пользователя).
        
        Args:
            id_value: Имя пользователя
            
        Returns:
            bool: True если пользователь был удален, иначе False
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == id_value)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return False
        
        await self.session.delete(user_model)
        await self.session.commit()
        return True 