import bcrypt
import secrets
import uuid
from datetime import datetime, timedelta
from jose import jwt

from infrastructure.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

async def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def create_tokens(data: dict) -> tuple[str, str]:
    """Create access and refresh JWT tokens."""
    access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token_data = {
        "sub": data["sub"],
        "exp": access_token_expires,
        "type": "access",
        "jti": str(uuid.uuid4())
    }
    access_token = jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)

    refresh_token_data = {
        "sub": data["sub"],
        "exp": refresh_token_expires,
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    refresh_token = jwt.encode(refresh_token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token

def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    return secrets.token_hex(16) 