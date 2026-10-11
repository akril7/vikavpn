import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db import connection
from src.db.models import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    """In-memory SQLite для одного теста. Схема создаётся заново."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(session_factory):
    """Готовая сессия для теста. Rollback после теста — изоляция."""
    async with session_factory() as s:
        yield s
        await s.rollback()


@pytest.fixture(autouse=True)
def _patch_connection(monkeypatch, engine, session_factory):
    """
    Подменяем глобальные engine и Session в src.db.connection,
    чтобы `async with Session() as s` в проде шло в SQLite.
    """
    monkeypatch.setattr(connection, "engine", engine)
    monkeypatch.setattr(connection, "Session", session_factory)
    yield


pytest_plugins = [
    "tests.fixtures.settings",
    "tests.fixtures.factories",
]
