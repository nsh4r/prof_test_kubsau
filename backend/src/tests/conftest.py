import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from backend.src.config import settings
from backend.src.database.main import get_session

# Используем строку подключения из настроек
DATABASE_URL = settings.postgres_url  # Получаем строку подключения из конфигов

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Сессия для тестовой базы
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="module")
async def session():
    """Создание сессии для теста"""
    # Создаем все таблицы в тестовой базе
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Создаем сессию
    session = TestingSessionLocal()

    yield session  # Передаем сессию в тесты

    # Очистка после завершения тестов
    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def client(session):
    """Фикстура для FastAPI клиента"""
    from fastapi.testclient import TestClient
    from backend.src.__init__ import app

    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)
