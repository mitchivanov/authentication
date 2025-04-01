from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

from infrastructure.config.settings import SECRET_KEY, ALGORITHM
from infrastructure.repositories.user_repository import UserRepository
from domain.entities.user import User
from infrastructure.config.database import get_session

# Используем правильный путь с префиксом /api для авторизации в Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(request: Request) -> Optional[User]:
    """Extract and validate the current user from request cookies or authorization header."""
    # Try to get token from cookies first
    token = request.cookies.get("access_token")
    
    # If not in cookies, try authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        
        if not username or token_type != "access":
            return None
        
        # Get user from database
        async for session in get_session():
            user_repo = UserRepository(session)
            user = await user_repo.get_by_username(username)
            return user
            
    except JWTError:
        return None

async def require_auth(request: Request) -> User:
    """Require authentication for a route."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def csrf_protect(request: Request, call_next):
    """Middleware for CSRF protection."""
    # Пропускаем проверку CSRF для запросов из Swagger UI
    if request.headers.get("referer") and "/docs" in request.headers.get("referer"):
        response = await call_next(request)
        return response
    
    if request.method in ("POST", "PUT", "DELETE"):
        cookie = request.cookies.get("csrf_token")
        header = request.headers.get("X-CSRF-Token")
        
        if not cookie or not header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="CSRF token missing"
            )
        
        from application.services.auth_service import AuthService
        from infrastructure.repositories.user_repository import UserRepository
        
        async for session in get_session():
            auth_service = AuthService(UserRepository(session))
            if not auth_service.verify_csrf_token(cookie, header):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid CSRF token"
                )
            break
    
    response = await call_next(request)
    return response 