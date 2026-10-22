from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.settings.app import DB_URL, DEBUG
from src.db.models import Base


def create_engine(url: str | None = None, *, echo: bool | None = None):
    return create_async_engine(
        url or DB_URL,
        echo=DEBUG if echo is None else echo,
        pool_pre_ping=True,
    )


def create_sessionmaker(eng) -> async_sessionmaker:
    return async_sessionmaker(eng, expire_on_commit=False)


engine = create_engine()
Session = create_sessionmaker(engine)


async def tables_exist() -> bool:
    async with engine.connect() as conn:
        return await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("users")
        )


async def create_tables():
    if await tables_exist():
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
