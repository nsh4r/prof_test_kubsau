# backend/src/tests/conftest.py
import pytest
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from backend.src.config import settings  # настройка подключения
from backend.src.__init__ import app

@pytest.fixture(scope="function")
async def session():
    """
    Фикстура для создания сессии для каждого теста.
    Создаем новый движок и сессию для тестов.
    """
    # создаем асинхронный движок для тестов
    engine = create_async_engine(settings.postgres_url, echo=False)

    # создаем таблицы для теста
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # создаем сессию
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # создаем сессию для выполнения запросов
    async with async_session() as session:
        yield session  # возвращаем сессию для теста

    # cleanup: удаляем все таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()  # закрываем движок

@pytest.fixture
async def client():
    """
    Фикстура для создания клиента HTTP для тестов.
    """
    async with AsyncClient(app=app, base_url=settings.postgres_url) as client:
        yield client
