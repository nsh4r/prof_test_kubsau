import asyncio
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.src.database.main import get_session
from backend.src.__init__ import app
from backend.src.config import settings

DATABASE_URL = settings.postgres_url

# engine + sessionmaker
test_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

# фикстура, чтобы избежать "attached to a different loop"
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# инициализация базы
@pytest.fixture(scope="function")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

# клиент + override зависимостей FastAPI
@pytest.fixture()
async def client(prepare_database):  # теперь БД инициализируется только при использовании client
    async def override_get_session():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
