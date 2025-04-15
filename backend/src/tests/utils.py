import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.src.config import settings


class TestConstants:
    """Test constants"""
    PHONE: str = '79000000000'
    NAME: str = 'Ivan'
    SURNAME: str = 'Ivanov'
    PATRONYMIC: str = 'Ivanovich'
    CITY: str = 'Krasnodar'


@pytest.fixture
async def async_engine():
    engine = create_async_engine(
        settings.postgres_url.replace("postgresql+asyncpg", "postgresql+asyncpg"),
        echo=True,
        future=True
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()

    # Drop all tables after tests
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)