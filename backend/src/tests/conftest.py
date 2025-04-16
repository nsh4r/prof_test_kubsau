import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.src.database.main import get_session
from backend.src.__init__ import app
from backend.src.config import settings

DATABASE_URL = settings.postgres_url

test_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac