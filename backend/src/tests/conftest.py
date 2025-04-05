import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.src.database.main import async_engine
from backend.src.__init__ import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def db_session():
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create a new session for testing
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    session = async_session()

    yield session

    # Clean up
    await session.close()
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)