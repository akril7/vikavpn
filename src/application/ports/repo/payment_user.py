from typing import Protocol

from src.domain.models import PaymentUser, Users


class PaymentUserRepoLike(Protocol):
    async def link(self, *, payment_id: int, user_id: int) -> PaymentUser:
        """Привязать одного пользователя к платежу."""
        ...

    async def link_many(
        self, *, payment_id: int, user_ids: list[int]
    ) -> list[PaymentUser]:
        """Привязать сразу несколько пользователей одним flush."""
        ...

    async def get_users(self, payment_id: int) -> Users:
        ...

    async def unlink(self, *, payment_id: int, user_id: int) -> bool:
        ...

    async def unlink_all(self, payment_id: int) -> int:
        ...
