"""
Доменные сервисы.

Этот модуль содержит доменные сервисы, которые реализуют бизнес-логику,
не привязанную к конкретным сущностям или работающие с несколькими сущностями.
"""

from domain.services.auth_service import AuthDomainService
from domain.services.user_service import UserDomainService

# Отмечаем user_domain_service.py как устаревший
# Импортируем только UserDomainService из user_service.py

__all__ = ["AuthDomainService", "UserDomainService"] 