from decimal import Decimal

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.enums import Tariff, PaymentStatus
from src.db.models import User, Payment
from src.db.repo.payment_user import PaymentUserRepository
from src.db.repo.user import UserRepository
from src.users.subscription import extend
from src.db.repo.payment import PaymentRepository
from src.core.payment.plans import get_plan
from src.core.utils.dt import utcnow
from src.core.url_build.link import build_payment_url


async def create_payment(
    session: AsyncSession,
    payer: User,
    targets: list[User],
    tariff: Tariff,
    days: int,
    receiver: str,
    fee_percent: float = 0
) -> tuple[Payment, str]:
    plan = get_plan(tariff, days)
    if plan is None:
        raise ValueError(f"Неизвестный тариф/срок: {tariff} {days}")

    base_amount = plan.price * len(targets)
    fee = Decimal(base_amount) * Decimal(fee_percent) / Decimal(100)
    amount = (Decimal(base_amount) + fee).quantize(Decimal("0.01"))

    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment = await payment_repo.create_payment(
        payer_id=payer.id,
        tariff=tariff,
        days=days,
        amount=amount
    )
    payment.label = f"{payer.uuid.hex}_{tariff.value}_{payment.id}"

    await link_repo.link_many(
        payment_id=payment.id,
        user_ids=[t.id for t in targets])

    await session.commit()

    url = build_payment_url(payment, receiver)

    return payment, url


async def confirm_payment(
    session: AsyncSession,
    label: str,
    amount: Decimal
) -> Payment | None:
    user_repo = UserRepository(session)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment = await payment_repo.get_by_label(label)
    if payment is None:
        logger.warning(f"Платёж с {label=} не найден")
        return None

    if payment.amount != amount:
        logger.warning(f"Платеж {payment.id} должен быть оплачен на {payment.amount}, а был на {amount}")
        return None

    if payment.status == PaymentStatus.PAID:
        logger.warning(f"Платёж {payment.id} уже оплачен")
        return payment

    payment.status = PaymentStatus.PAID
    payment.paid_at = utcnow()

    user_ids = await link_repo.get_user_ids(payment.id)
    if not user_ids:
        logger.warning(f"Платёж {payment.id} не имеет привязанных пользователей")

    for user_id in user_ids:
        target = await user_repo.get(user_id)
        if target is None:
            logger.warning(f"Пользователь {user_id} не найден, пропускаем")
            continue
        extend(target, payment.tariff, payment.days)

    await session.commit()
    logger.info(f"Платёж {payment.id} подтверждён, продлено {len(user_ids)} подписок")
    return payment
