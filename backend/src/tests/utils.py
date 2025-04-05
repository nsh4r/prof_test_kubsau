from typing import Final
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.main import async_engine

class TestConstants:
    """Test constants"""
    PHONE: Final[str] = '79000000000'
    NAME: Final[str] = 'Ivan'
    SURNAME: Final[str] = 'Ivanov'
    PATRONYMIC: Final[str] = 'Ivanovich'
    CITY: Final[str] = 'Moscow'

# Async test session
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_test_session() -> AsyncSession:
    async with async_session() as session:
        yield session