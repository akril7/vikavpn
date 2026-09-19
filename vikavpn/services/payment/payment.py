from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from database.crud import get_payment_by_label, get_payment_user_ids
from database.models import Payment, PaymentStatus, User, Tariff
from services.link import build_payment_url
from services.payment.plans import get_plan
from services.subscription import extend_subscription


async def create_payment(
    session: AsyncSession,
    payer: User,
    targets: list[User],
    tariff: Tariff,
    days: int,
    receiver: str,
) -> tuple[Payment, str]:
    plan = get_plan(tariff, days)
    if plan is None:
        raise ValueError(f"Неизвестный тариф/срок: {tariff} {days}")

    amount = plan.price * len(targets)

    payment = await crud.create_payment(session, payer.id, tariff, days, amount)
    await session.flush()

    payment.label = f"{payer.uuid.hex}_{tariff.value}_{payment.id}"

    for target in targets:
        await crud.create_payment_user(session, payment.id, target.id)

    await session.commit()

    url = build_payment_url(payment, receiver)
    return payment, url


async def confirm_payment(
    session: AsyncSession,
    label: str
) -> Payment | None:
    payment = await get_payment_by_label(session, label)
    if payment is None:
        logger.warning(f"Платёж с label={label} не найден")
        return None

    if payment.status == PaymentStatus.PAID:
        logger.warning(f"Платёж {payment.id} уже оплачен")
        return payment

    payment.status = PaymentStatus.PAID
    payment.paid_at = datetime.now()
    await session.commit()

    user_ids = await get_payment_user_ids(session, payment.id)
    for user_id in user_ids:
        target: User | None = await session.get(User, user_id)
        if target is not None:
            await extend_subscription(session, target, payment.tariff, payment.days)

    return payment
