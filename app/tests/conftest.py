import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app


sqlite_url = 'sqlite+aiosqlite:///:memory:'


test_engin = create_async_engine(
    sqlite_url,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSettionLocal = sessionmaker(
    bind=test_engin,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_db():
    async with test_engin.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engin.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSettionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
