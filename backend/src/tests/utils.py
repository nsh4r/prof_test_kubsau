from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.src.config import settings

async_engine = create_async_engine(settings.postgres_url)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


class TestConstants:
    """Test constants"""
    PHONE: str = '79000000000'
    UUID: str = 'a1b2c3d4-e5f6-7890-1234-56789abcdef0'