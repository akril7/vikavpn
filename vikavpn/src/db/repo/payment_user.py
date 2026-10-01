from sqlalchemy import select, delete as sql_delete

from src.db.models import PaymentUser, User
from src.db.repo.base import BaseRepository


class PaymentUserRepository(BaseRepository[PaymentUser]):
    model = PaymentUser

    async def link(self, *, payment_id: int, user_id: int) -> PaymentUser:
        """Привязать одного пользователя к платежу."""
        link = PaymentUser(payment_id=payment_id, user_id=user_id)
        self.session.add(link)
        await self.session.flush()
        return link

    async def link_many(
        self, *, payment_id: int, user_ids: list[int]
    ) -> list[PaymentUser]:
        """Привязать сразу несколько пользователей одним flush."""
        links = [
            PaymentUser(payment_id=payment_id, user_id=uid)
            for uid in user_ids
        ]
        self.session.add_all(links)
        await self.session.flush()
        return links

    async def get_user_ids(self, payment_id: int) -> list[int]:
        stmt = (
            select(PaymentUser.user_id)
            .where(PaymentUser.payment_id == payment_id)
        )
        return list((await self.session.scalars(stmt)).all())

    async def get_users(self, payment_id: int) -> list[User]:
        stmt = (
            select(User)
            .join(PaymentUser, PaymentUser.user_id == User.id)
            .where(PaymentUser.payment_id == payment_id)
            .order_by(User.id)
        )
        return list((await self.session.scalars(stmt)).all())

    async def unlink(self, *, payment_id: int, user_id: int) -> bool:
        stmt = sql_delete(PaymentUser).where(
            PaymentUser.payment_id == payment_id,
            PaymentUser.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        return result.rowcount > 0

    async def unlink_all(self, payment_id: int) -> int:
        stmt = sql_delete(PaymentUser).where(PaymentUser.payment_id == payment_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        return result.rowcount
