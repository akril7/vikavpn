from datetime import datetime

from src.domain.models import User
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository


async def load_active_users() -> list[User]:
    """Адаптер порта UserLoader: активные пользователи из БД."""
    async with Session() as session:
        return await UserRepository(session).list_active()


async def load_next_expire_at() -> datetime | None:
    async with Session() as session:
        return await UserRepository(session).get_next_expire_at()
