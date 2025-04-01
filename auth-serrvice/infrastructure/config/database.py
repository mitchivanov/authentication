from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator

from infrastructure.config.settings import DATABASE_URL

Base = declarative_base()

# Create async engine for the database
engine = create_async_engine(DATABASE_URL)

# Create sessionmaker
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    """Initialize the database, creating tables if needed."""
    # Импортируем модели, чтобы они были зарегистрированы в метаданных Base
    from infrastructure.database.models.user_model import UserModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with async_session() as session:
        yield session 