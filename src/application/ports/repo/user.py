from typing import Protocol, Any
from uuid import UUID

from src.domain.models import User


class UserRepoLike(Protocol):
    async def create(self, **values: Any) -> User:
        ...

    async def get_by_name(self, name: str) -> User | None:
        ...

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        ...

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        ...
