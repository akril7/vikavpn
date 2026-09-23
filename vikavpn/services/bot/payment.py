from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_payment_by_label
from database.models import Payment, PaymentStatus, Tariff, User
from services.payment.payment import create_payment as _create_payment


class PaymentCheckResult(StrEnum):
    NOT_FOUND = "not_found"
    NOT_PAID = "not_paid"
    PAID = "paid"


async def start_payment(
    session: AsyncSession,
    payer: User,
    targets: list[User],
    tariff: Tariff,
    days: int,
    receiver: str,
) -> tuple[Payment, str]:
    return await _create_payment(
        session=session,
        payer=payer,
        targets=targets,
        tariff=tariff,
        days=days,
        receiver=receiver,
    )


async def check_payment(
    session: AsyncSession,
    label: str,
) -> tuple[PaymentCheckResult, Payment | None]:
    payment = await get_payment_by_label(session, label)
    if payment is None:
        return PaymentCheckResult.NOT_FOUND, None
    if payment.status != PaymentStatus.PAID or payment.paid_at is None:
        return PaymentCheckResult.NOT_PAID, payment
    return PaymentCheckResult.PAID, payment
