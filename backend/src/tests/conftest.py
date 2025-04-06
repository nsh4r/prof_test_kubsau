import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from backend.src.__init__ import app
from backend.src.config import settings


@pytest.fixture(scope="session")
async def engine():
    # Используем тестовую БД с тем же пользователем, что и в основном приложении
    test_db_url = settings.postgres_url.replace(
        f"/{settings.DB_NAME}",
        f"/{settings.DB_NAME}_test"
    )

    engine = create_async_engine(test_db_url, echo=True)

    # Создаем тестовую БД (если еще не существует)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Очищаем после всех тестов
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()  # Откатываем несохраненные изменения


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
async def override_dependencies(session):
    from backend.src.database.main import get_session

    async def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()