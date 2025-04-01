from fastapi import HTTPException, status
from typing import Dict, Any, Optional
from datetime import date

from domain.entities.user import User
from domain.services.user_service import UserDomainService
from domain.schemas.user import UserInfoSchema
from domain.interfaces.repositories import UserRepositoryInterface
from infrastructure.utils.security import hash_password

class UserApplicationService:
    """
    Сервис приложения для работы с пользователями.
    
    Реализует сценарии использования, связанные с управлением
    пользователями, оркестрируя взаимодействие между доменными
    сервисами и репозиториями.
    """
    
    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Инициализировать сервис с репозиторием пользователей.
        
        Args:
            user_repository: Репозиторий для работы с пользователями
        """
        self.user_repository = user_repository
        self.domain_service = UserDomainService()
    
    async def register_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        date_of_birth: date
    ) -> UserInfoSchema:
        """
        Зарегистрировать нового пользователя.
        
        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль
            date_of_birth: Дата рождения
            
        Returns:
            UserInfoSchema: Зарегистрированный пользователь
            
        Raises:
            HTTPException: Если регистрация не удалась
        """
        # Проверяем, что пользователь с таким именем не существует
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким именем уже существует"
            )
        
        # Проверяем, что пользователь с таким email не существует
        existing_email = await self.user_repository.get_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
        
        # Проверяем бизнес-правила для регистрации
        validation_errors = self.domain_service.validate_registration(
            username=username,
            email=email,
            password=password,
            date_of_birth=date_of_birth
        )
        
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": validation_errors}
            )
        
        # Хешируем пароль
        password_hash = await hash_password(password)
        
        # Создаем доменную сущность
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            date_of_birth=date_of_birth,
            bank_balance=0.0
        )
        
        # Сохраняем пользователя через репозиторий
        created_user = await self.user_repository.create(user)
        
        # Преобразуем сущность в схему ответа
        return UserInfoSchema(
            username=created_user.username,
            email=created_user.email,
            date_of_birth=created_user.date_of_birth
        )
    
    async def get_user_by_username(self, username: str) -> UserInfoSchema:
        """
        Получить информацию о пользователе по имени пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            UserInfoSchema: Информация о пользователе
            
        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return UserInfoSchema(
            username=user.username,
            email=user.email,
            date_of_birth=user.date_of_birth
        )
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Получить расширенную информацию о пользователе.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Dict[str, Any]: Расширенная информация о пользователе
            
        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return {
            "username": user.username,
            "email": user.email,
            "date_of_birth": user.date_of_birth,
            "age": user.age,
            "is_adult": user.is_adult
        }
    
    async def update_user(
        self, 
        username: str, 
        email: Optional[str] = None,
        password: Optional[str] = None,
        date_of_birth: Optional[date] = None
    ) -> UserInfoSchema:
        """
        Обновить информацию о пользователе.
        
        Args:
            username: Имя пользователя
            email: Новый email
            password: Новый пароль
            date_of_birth: Новая дата рождения
            
        Returns:
            UserInfoSchema: Обновленный пользователь
            
        Raises:
            HTTPException: Если пользователь не найден или данные некорректны
        """
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Обновляем поля, если они предоставлены
        if email is not None:
            # Проверяем, что такой email не занят другим пользователем
            existing_email = await self.user_repository.get_by_email(email)
            if existing_email and existing_email.username != username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким email уже существует"
                )
            user.email = email
        
        if password is not None:
            # Проверяем, что пароль соответствует требованиям
            password_errors = user.validate_password(password)
            if password_errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"errors": password_errors}
                )
            user.password_hash = await hash_password(password)
        
        if date_of_birth is not None:
            user.date_of_birth = date_of_birth
            
            # Проверяем валидность даты рождения
            validation_errors = user.validate()
            if validation_errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"errors": validation_errors}
                )
        
        # Сохраняем обновленного пользователя
        updated_user = await self.user_repository.update(user)
        
        # Преобразуем сущность в схему ответа
        return UserInfoSchema(
            username=updated_user.username,
            email=updated_user.email,
            date_of_birth=updated_user.date_of_birth
        )
    
    async def delete_user(self, username: str) -> Dict[str, str]:
        """
        Удалить пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Dict[str, str]: Сообщение об успешном удалении
            
        Raises:
            HTTPException: Если пользователь не найден
        """
        deleted = await self.user_repository.delete(username)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return {"message": "Пользователь успешно удален"} 