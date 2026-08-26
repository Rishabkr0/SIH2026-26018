import os
# Must set these before any app imports so Settings() does not fail with missing required fields.
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://bhulekh_user:bhulekh_password@postgres:5432/bhulekh_test"
os.environ["REDIS_URL"] = "redis://redis:6379/1"
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin123")

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.main import app as fastapi_app
from app.db.session import engine as test_engine, AsyncSessionLocal
from app.db.base import Base
from app import models  # Ensure all models are registered with Base

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    sys_engine = create_async_engine(
        "postgresql+asyncpg://bhulekh_user:bhulekh_password@postgres:5432/bhulekh_db",
        isolation_level="AUTOCOMMIT"
    )
    async with sys_engine.connect() as conn:
        try:
            await conn.execute(text("CREATE DATABASE bhulekh_test"))
        except Exception:
            pass
    await sys_engine.dispose()
    
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(autouse=True)
async def clear_tables():
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield

from app.db.redis_client import redis_client

@pytest_asyncio.fixture(autouse=True)
async def setup_redis():
    await redis_client.connect()
    if redis_client.redis:
        await redis_client.redis.flushdb()
    yield
    if redis_client.redis:
        await redis_client.redis.flushdb()
    await redis_client.close()

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
def test_pdf():
    return b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%EOF\n"
