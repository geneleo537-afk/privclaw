"""
Pytest 配置与共享 fixtures。

提供数据库、HTTP 客户端、认证用户等可复用 fixtures。
"""
import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.core.database import get_db
from app.main import app


TEST_DATABASE_URL = "postgresql+asyncpg://privclaw:privclaw123@localhost:5432/privclaw_test"


@pytest.fixture(scope="session")
def event_loop():
    """创建 session 级别的事件循环，供所有异步测试共享。"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """返回测试环境配置。"""
    from app.core.encryption import DataEncryption
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        APP_ENV="testing",
        APP_DEBUG=True,
        APP_SECRET_KEY="test-secret-key-for-pytest-only",
        JWT_SECRET="test-jwt-secret-for-pytest-only",
        REDIS_URL="redis://localhost:6379/10",
        DATA_ENCRYPTION_KEY=DataEncryption.generate_key(),
    )


@pytest_asyncio.fixture(scope="session")
async def engine():
    """创建测试数据库引擎。"""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="session")
async def setup_database(engine):
    """创建所有测试表。"""
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(engine, setup_database) -> AsyncGenerator[AsyncSession, None]:
    """为每个测试创建独立的数据库 session，测试后回滚。"""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """创建异步 HTTP 客户端，注入测试数据库 session。"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncGenerator[tuple[AsyncClient, dict], None]:
    """创建已认证的 HTTP 客户端，返回 (client, user_data)。"""
    register_data = {
        "email": "test@example.com",
        "password": "Test123456",
        "nickname": "TestUser",
    }
    resp = await client.post("/api/v1/auth/register", json=register_data)
    assert resp.status_code == 201
    tokens = resp.json()["data"]

    client.headers["Authorization"] = f"Bearer {tokens['access_token']}"
    yield client, tokens

    client.headers.pop("Authorization", None)
