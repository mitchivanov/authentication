from sqlalchemy import Column, String, Date, Numeric
from infrastructure.config.database import Base
from datetime import datetime, date
from decimal import Decimal

class User(Base):
    """
    Доменная модель пользователя.
    
    Представляет пользователя системы и содержит бизнес-логику, 
    связанную с пользователем.
    """
    __tablename__ = "users"
    
    username = Column(String, primary_key=True)
    password_hashed = Column(String)
    email = Column(String)
    date_of_birth = Column(Date)
    bank_balance = Column(Numeric(10, 2))
    
    @property
    def age(self) -> int:
        """Вычислить возраст пользователя на основе даты рождения."""
        if not self.date_of_birth:
            return 0
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_adult(self) -> bool:
        """Проверить, является ли пользователь совершеннолетним (18+)."""
        return self.age >= 18
    
    def can_withdraw(self, amount: Decimal) -> bool:
        """
        Проверить, может ли пользователь снять указанную сумму со счета.
        
        Args:
            amount: Сумма для снятия
            
        Returns:
            bool: True, если пользователь может снять указанную сумму, иначе False
        """
        # Бизнес-правило: нельзя снять больше, чем есть на счете
        if self.bank_balance is None:
            return False
        return self.bank_balance >= amount 