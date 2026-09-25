from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from database.enums import Tariff, PaymentStatus
from database.models import User, Users, Payment
from database.repo.payment import PaymentRepository
from services.payment import create_payment


class PaymentCheckResult(StrEnum):
    NOT_FOUND = "not_found"
    NOT_PAID = "not_paid"
    PAID = "paid"


async def start_payment(
    session: AsyncSession,
    payer: User,
    targets: Users,
    tariff: Tariff,
    days: int,
    receiver: str,
    fee_percent: float
) -> tuple[Payment, str]:
    return await create_payment(
        session=session,
        payer=payer,
        targets=targets,
        tariff=tariff,
        days=days,
        receiver=receiver,
        fee_percent=fee_percent
    )


async def check_payment(
    session: AsyncSession,
    label: str,
) -> tuple[PaymentCheckResult, Payment | None]:
    repo = PaymentRepository(session)

    payment = await repo.get_by_label(label)
    if payment is None:
        return PaymentCheckResult.NOT_FOUND, None
    if payment.status != PaymentStatus.PAID or payment.paid_at is None:
        return PaymentCheckResult.NOT_PAID, payment
    return PaymentCheckResult.PAID, payment
