from decimal import Decimal

from loguru import logger

from src.domain.enums import Tariff, PaymentStatus
from src.domain.models import User, Payment, Users
from src.domain.payment.plans import get_plan
from src.domain.users import subscription

from src.application.ports.repo import PaymentRepoLike, PaymentUserRepoLike


async def create_payment(
    payment_repo: PaymentRepoLike,
    link_repo: PaymentUserRepoLike,
    payer: User,
    targets: Users,
    tariff: Tariff,
    days: int,
    fee_percent: float = 0
) -> Payment:
    """
    Создать платёж для продления подписки одной или нескольких целей.

    Рассчитывает сумму как ``plan.price * len(targets)`` плюс комиссия
    ``fee_percent``, создаёт запись ``Payment`` со статусом ``PENDING``
    и привязывает к нему список целевых пользователей. Дополнительно
    формирует уникальный ``label`` (используется для сверки с вебхуком
    ЮMoney) и URL для оплаты.

    Запись платежа и связи добавляются в сессию через ``flush``, но
    **не коммитятся** — коммит выполняет вызывающий код.

    Args:
        payment_repo: Репозиторий для создания платежа.
        link_repo: Репозиторий для привязки целей к платежу.
        payer: Плательщик (кто инициирует оплату).
        targets: Пользователи, которым будет продлена подписка.
            Не должен быть пустым.
        tariff: Тариф (``PROXY`` или ``FULL``), влияет на цену.
        days: Срок продления в днях, должен соответствовать одному
            из ``PLANS`` для выбранного тарифа.
        fee_percent: Процент комиссии, добавляемый к базовой сумме.
            По умолчанию ``0.0``.

    Raises:
        ValueError: Если ``targets`` пустой или для пары
            ``(tariff, days)`` не найден подходящий план.
    """
    if not targets:
        raise ValueError("Пустой targets")

    plan = get_plan(tariff, days)
    if plan is None:
        raise ValueError(f"Неизвестный тариф/срок: {tariff} {days}")

    base_amount = plan.price * len(targets)
    fee = Decimal(base_amount) * Decimal(fee_percent) / Decimal(100)
    amount = (Decimal(base_amount) + fee).quantize(Decimal("0.01"))

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

    return payment


async def confirm_payment(
    payment_repo: PaymentRepoLike,
    link_repo: PaymentUserRepoLike,
    label: str,
    amount: Decimal,
) -> Payment | None:
    """Подтвердить платёж по вебхуку и продлить подписки целей.

    Идемпотентна: повторный вызов с тем же ``label`` для уже оплаченного
    платежа вернёт его без повторного продления. Если сумма не совпадает
    или платёж не найден — возвращает ``None`` и логирует причину.

    Атомарность подтверждения обеспечивается методом
    ``PaymentRepository.mark_paid_if_pending`` (``UPDATE ... RETURNING``),
    что исключает гонку при параллельных вебхуках.

    ...

    Returns:
        Подтверждённый ``Payment`` при успехе. ``None``, если платёж
        не найден, сумма не совпала или он уже был подтверждён другим
        параллельным вызовом.
    """
    payment = await payment_repo.get_by_label(label)
    if payment is None:
        logger.warning(f"Платёж с {label=} не найден")
        return None

    if payment.amount != amount:
        logger.warning(
            f"Платёж {payment.id} должен быть оплачен на "
            f"{payment.amount}, а был на {amount}"
        )
        return None

    if payment.status == PaymentStatus.PAID:
        logger.info(f"Платёж {payment.id} уже оплачен (повторный вебхук)")
        return payment

    paid = await payment_repo.mark_paid_if_pending(label, amount)
    if paid is None:
        logger.info(f"Платёж {payment.id} подтверждён параллельным вызовом")
        return await payment_repo.get_by_label(label)

    users = await link_repo.get_users(paid.id)
    if not users:
        logger.warning(f"Платёж {paid.id} не имеет привязанных пользователей")

    for target in users:
        subscription.extend(target, paid.tariff, paid.days)

    logger.info(
        f"Платёж {paid.id} подтверждён, продлено {len(users)} подписок"
    )
    return paid


async def get_paid_payment(
    repo: PaymentRepoLike,
    label: str,
) -> Payment | None:
    payment = await repo.get_by_label(label)
    if payment is None or payment.status != PaymentStatus.PAID or payment.paid_at is None:
        return None
    return payment
