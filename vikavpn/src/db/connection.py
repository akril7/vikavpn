from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.settings.app import DB_URL, DEBUG
from src.db.models import Base

engine = create_async_engine(DB_URL, echo=DEBUG)

Session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
