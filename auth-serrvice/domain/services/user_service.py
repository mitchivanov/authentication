from datetime import date
from decimal import Decimal
from typing import List, Optional

from domain.entities.user import User

class UserDomainService:
    """
    Доменный сервис для работы с пользователями.
    
    Содержит бизнес-логику, которая не привязана к конкретной
    сущности User или затрагивает несколько сущностей.
    """
    
    @staticmethod
    def validate_registration(
        username: str, 
        email: str, 
        password: str, 
        date_of_birth: date
    ) -> List[str]:
        """
        Валидировать данные для регистрации пользователя.
        
        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль
            date_of_birth: Дата рождения
            
        Returns:
            List[str]: Список ошибок валидации, пустой если ошибок нет
        """
        errors = []
        
        # Проверка возраста
        today = date.today()
        age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
        
        if age < 18:
            errors.append("Пользователь должен быть совершеннолетним (18+)")
        
        # Создаем временный объект для проверки валидации
        temp_user = User(
            username=username,
            email=email,
            password_hash=password,
            date_of_birth=date_of_birth
        )
        
        # Добавляем ошибки валидации объекта
        errors.extend(temp_user.validate())
        
        # Добавляем ошибки валидации пароля
        errors.extend(temp_user.validate_password(password))
        
        return errors
    
    @staticmethod
    def calculate_withdrawal_fee(user: User, amount: Decimal) -> Decimal:
        """
        Рассчитать комиссию за снятие средств.
        
        Args:
            user: Пользователь
            amount: Сумма для снятия
            
        Returns:
            Decimal: Комиссия за снятие
        """
        # Пример бизнес-правила: комиссия 1%, но для пользователей старше 60 лет - 0%
        if user.age > 60:
            return Decimal('0')
        
        return amount * Decimal('0.01')
    
    @staticmethod
    def can_transfer(
        sender: User, 
        recipient: User, 
        amount: Decimal
    ) -> bool:
        """
        Проверить, может ли один пользователь перевести средства другому.
        
        Args:
            sender: Отправитель
            recipient: Получатель
            amount: Сумма перевода
            
        Returns:
            bool: True если перевод возможен, иначе False
        """
        # Пример сложной бизнес-логики, затрагивающей несколько сущностей
        
        # Проверяем, что у отправителя достаточно средств
        if not sender.can_withdraw(amount):
            return False
        
        # Проверяем, что получатель может принимать средства (например, не заблокирован)
        if not recipient:
            return False
        
        # Другие бизнес-правила для переводов...
        
        return True 