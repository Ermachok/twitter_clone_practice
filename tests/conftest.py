import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.base import Base
from app.database import get_db
from app.models.user import User
from app.models.follow import Follow
from app.models.tweet import Tweet
from app.models.like import Like


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def setup_database():
    """Создаёт таблицы перед тестами и удаляет после"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_session(setup_database):
    """Создаёт новую асинхронную сессию БД для тестов"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_session):
    """Асинхронный клиент FastAPI с тестовой БД"""
    app.dependency_overrides[get_db] = lambda: test_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

