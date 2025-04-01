import hmac
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class AuthDomainService:
    """
    Доменный сервис для аутентификации и авторизации.
    
    Содержит бизнес-логику, связанную с аутентификацией пользователей,
    которая не зависит от конкретной технологии хранения или фреймворка.
    """
    
    @staticmethod
    def verify_csrf_token(token1: str, token2: str) -> bool:
        """
        Проверить соответствие CSRF токенов.
        
        Использует постоянное время сравнения для защиты от timing-атак.
        
        Args:
            token1: Первый токен
            token2: Второй токен
            
        Returns:
            bool: True если токены совпадают, иначе False
        """
        return hmac.compare_digest(token1, token2)
    
    @staticmethod
    def is_token_expired(expiration_time: datetime) -> bool:
        """
        Проверить, истек ли срок действия токена.
        
        Args:
            expiration_time: Время истечения срока действия
            
        Returns:
            bool: True если токен истек, иначе False
        """
        return datetime.utcnow() > expiration_time
    
    @staticmethod
    def calculate_token_expiry(
        token_type: str, 
        minutes: Optional[int] = None, 
        days: Optional[int] = None
    ) -> datetime:
        """
        Рассчитать время истечения срока действия токена.
        
        Args:
            token_type: Тип токена ('access' или 'refresh')
            minutes: Срок действия в минутах (для access токена)
            days: Срок действия в днях (для refresh токена)
            
        Returns:
            datetime: Время истечения срока действия
        """
        now = datetime.utcnow()
        
        if token_type == "access":
            return now + timedelta(minutes=minutes or 60)
        elif token_type == "refresh":
            return now + timedelta(days=days or 7)
        else:
            raise ValueError(f"Неизвестный тип токена: {token_type}")
            
    @staticmethod
    def should_refresh_token(expiration_time: datetime, threshold_minutes: int = 5) -> bool:
        """
        Определить, нужно ли обновить токен.
        
        Args:
            expiration_time: Время истечения срока действия
            threshold_minutes: Пороговое значение в минутах
            
        Returns:
            bool: True если токен следует обновить, иначе False
        """
        time_left = expiration_time - datetime.utcnow()
        threshold = timedelta(minutes=threshold_minutes)
        
        return time_left < threshold 