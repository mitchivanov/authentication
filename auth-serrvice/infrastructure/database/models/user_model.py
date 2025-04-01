from sqlalchemy import Column, String, Date, Numeric
from decimal import Decimal
from datetime import date
from typing import Optional

from infrastructure.config.database import Base
from domain.entities.user import User

class UserModel(Base):
    """
    ORM-модель пользователя для работы с базой данных.
    
    Представляет таблицу пользователей в базе данных.
    Отделена от доменной модели для избежания зависимости доменного
    слоя от конкретных технологий хранения данных.
    """
    __tablename__ = "users"
    
    username = Column(String, primary_key=True)
    password_hashed = Column(String)
    email = Column(String)
    date_of_birth = Column(Date)
    bank_balance = Column(Numeric(10, 2))
    
    @classmethod
    def from_entity(cls, user: User) -> "UserModel":
        """
        Создать ORM-модель из доменной сущности.
        
        Args:
            user: Доменная сущность пользователя
            
        Returns:
            UserModel: ORM-модель для сохранения в БД
        """
        return cls(
            username=user.username,
            password_hashed=user.password_hash,
            email=user.email,
            date_of_birth=user.date_of_birth,
            bank_balance=user.bank_balance
        )
    
    def to_entity(self) -> User:
        """
        Преобразовать ORM-модель в доменную сущность.
        
        Returns:
            User: Доменная сущность пользователя
        """
        return User(
            username=self.username,
            email=self.email,
            password_hash=self.password_hashed,
            date_of_birth=self.date_of_birth,
            bank_balance=self.bank_balance if self.bank_balance is not None else Decimal('0.00')
        ) 