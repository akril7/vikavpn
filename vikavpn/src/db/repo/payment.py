from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.db.enums import Tariff
from src.db.models import Payment
from src.db.repo.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    # ─────────── Создание ───────────

    async def create_payment(
        self,
        *,
        payer_id: int,
        tariff: Tariff,
        days: int,
        amount: Decimal,
        label: str | None = None,
    ) -> Payment:
        payment = Payment(
            payer_id=payer_id,
            tariff=tariff,
            days=days,
            amount=amount,
            label=label,
        )
        self.session.add(payment)
        await self.session.flush()
        return payment

    # ─────────── Поиск ───────────

    async def get_by_label(self, label: str) -> Payment | None:
        stmt = select(Payment).where(Payment.label == label)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_with_users(self, payment_id: int) -> Payment | None:
        """Платёж + все привязанные пользователи."""
        stmt = (
            select(Payment)
            .where(Payment.id == payment_id)
            .options(selectinload(Payment.users))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_label_with_users(self, label: str) -> Payment | None:
        stmt = (
            select(Payment)
            .where(Payment.label == label)
            .options(selectinload(Payment.users))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Списки ───────────

    async def list_by_payer(
        self, payer_id: int, *, limit: int = 100, offset: int = 0
    ) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.payer_id == payer_id)
            .order_by(Payment.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.scalars(stmt)).all())
