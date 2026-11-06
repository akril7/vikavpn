from decimal import Decimal

from sqlalchemy import select, update

from src.domain.utils.dt import utcnow
from src.domain.enums import Tariff, PaymentStatus
from src.domain.models import Payment
from src.application.ports.repo import PaymentRepoLike
from src.infrastructure.persistence.repo.base import BaseRepository


class PaymentRepository(PaymentRepoLike, BaseRepository[Payment]):
    model = Payment

    # ─────────── Создание ───────────

    async def create_payment(
            self,
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

    # ─────────── Pending ───────────
    async def mark_paid_if_pending(self, label: str, amount: Decimal) -> Payment | None:
        """Атомарно пометить платёж оплаченным, если он ещё ``PENDING``. """
        stmt = (
            update(Payment)
            .where(
                Payment.label == label,
                Payment.amount == amount,
                Payment.status != PaymentStatus.PAID,
            )
            .values(
                status=PaymentStatus.PAID,
                paid_at=utcnow(),
            )
            .returning(Payment)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
