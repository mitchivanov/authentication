from datetime import date
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class User:
    """
    Доменная сущность пользователя.
    
    Представляет пользователя в системе и содержит бизнес-логику,
    связанную с пользователем.
    """
    username: str
    email: str
    password_hash: str
    date_of_birth: Optional[date] = None
    bank_balance: Optional[Decimal] = None
    
    @property
    def age(self) -> int:
        """
        Рассчитать возраст пользователя.
        
        Returns:
            int: Возраст пользователя в годах
        """
        if not self.date_of_birth:
            return 0
            
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_adult(self) -> bool:
        """
        Проверить, является ли пользователь совершеннолетним.
        
        Returns:
            bool: True если пользователь совершеннолетний (18+), иначе False
        """
        return self.age >= 18
    
    def validate_password(self, password: str) -> List[str]:
        """
        Проверить пароль на соответствие требованиям безопасности.
        
        Args:
            password: Пароль для проверки
            
        Returns:
            List[str]: Список ошибок, пустой если пароль валидный
        """
        errors = []
        
        if len(password) < 8 or len(password) > 20:
            errors.append("Пароль должен содержать от 8 до 20 символов")
            
        if not any(c.islower() for c in password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")
            
        if not any(c.isupper() for c in password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")
            
        if not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать хотя бы одну цифру")
            
        if not any(c in '@$!%*?&#' for c in password):
            errors.append("Пароль должен содержать хотя бы один спецсимвол (@$!%*?&#)")
            
        return errors
    
    def can_withdraw(self, amount: Decimal) -> bool:
        """
        Проверить, может ли пользователь снять указанную сумму.
        
        Args:
            amount: Сумма для снятия
            
        Returns:
            bool: True если у пользователя достаточно средств, иначе False
        """
        if self.bank_balance is None:
            return False
            
        return self.bank_balance >= amount
    
    def validate(self) -> List[str]:
        """
        Валидировать объект пользователя.
        
        Returns:
            List[str]: Список ошибок валидации, пустой если пользователь валидный
        """
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append("Имя пользователя должно содержать не менее 3 символов")
            
        if not self.email or '@' not in self.email:
            errors.append("Email должен быть действительным адресом")
            
        if not self.password_hash:
            errors.append("Пароль должен быть установлен")
            
        if self.date_of_birth and self.date_of_birth > date.today():
            errors.append("Дата рождения не может быть в будущем")
            
        return errors 