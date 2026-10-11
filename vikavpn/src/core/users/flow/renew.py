from enum import StrEnum

from src.core.payment.lifecycle import create_payment
from src.db.enums import Tariff
from src.db.models import Payment
from src.db.repo import UserRepository, PaymentRepository, PaymentUserRepository, options


class RenewError(Exception):
    """Базовая ошибка продления с сообщением для пользователя.

    Attributes:
        message: Текст, который можно показать пользователю в UI
            (например, через ``call.answer(..., show_alert=True)``).
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PayerNotFoundError(RenewError):
    """Плательщик не найден по Telegram ID.

    Возникает, если пользователь не авторизован или был удалён.
    """

    def __init__(self):
        super().__init__("Пользователь не найден")


class TargetNotFoundError(RenewError):
    """Целевой пользователь не найден среди управляемых.

    Возникает, если ``target_id`` не передан для ``RenewMode.OTHER``
    или не соответствует ни одному из ``managed_links`` плательщика.
    """

    def __init__(self):
        super().__init__("Пользователь не найден")


class RenewMode(StrEnum):
    SELF = "self"
    SELF_AND_MANAGED = "self_and_managed"
    OTHER = "other"


async def create_payment_for_renew(
    user_repo: UserRepository,
    payment_repo: PaymentRepository,
    link_repo: PaymentUserRepository,
    telegram_id: int,
    mode: RenewMode,
    tariff: Tariff,
    days: int,
    receiver: str,
    fee_percent: float = 0,
    target_id: int | None = None
) -> tuple[Payment, str]:
    """
    Создать платёж для продления подписки.

    Определяет цели продления по режиму (``mode``), создаёт платёж
    с рассчитанной суммой и возвращает его вместе с URL для оплаты.
    Сумма рассчитывается как ``plan.price * len(targets)`` с учётом
    ``fee_percent``.

    Запись платежа добавляется в сессию через ``flush``, но **не
    коммитится** — коммит выполняет вызывающий код.

    Args:
        user_repo: Репозиторий пользователей (поиск плательщика и целей).
        payment_repo: Репозиторий платежей (создание записи ``Payment``).
        link_repo: Репозиторий связей платёж-пользователь
            (привязка целей к платежу).
        telegram_id: Telegram ID плательщика.
        mode: Режим продления (``SELF``, ``SELF_AND_MANAGED`` или ``OTHER``).
        tariff: Тариф (``PROXY`` или ``FULL``), влияет на цену.
        days: Срок продления в днях, должен соответствовать одному
            из ``PLANS`` для выбранного тарифа.
        receiver: Кошелёк ЮMoney для приёма платежа.
        fee_percent: Процент комиссии, добавляемый к базовой сумме.
            По умолчанию ``0``.
        target_id: ID целевого пользователя. Обязателен для
            ``RenewMode.OTHER``, игнорируется в остальных режимах.

    Returns:
        Кортеж ``(payment, url)``, где ``payment`` — созданный платёж
        со статусом ``PENDING``, ``url`` — ссылка на оплату в ЮMoney.

    Raises:
        PayerNotFoundError: Плательщик с указанным ``telegram_id``
            не найден.
        TargetNotFoundError: Для ``RenewMode.OTHER`` не передан
            ``target_id`` или он не соответствует ни одному
            управляемому пользователю.
        ValueError: Неизвестный режим продления или тариф/срок
            не соответствует ни одному из ``PLANS``.
    """
    payer = await user_repo.get_by_telegram_id(telegram_id, options=options.managed_options())
    if payer is None:
        raise PayerNotFoundError

    if mode == RenewMode.SELF:
        targets = [payer]
    elif mode == RenewMode.SELF_AND_MANAGED:
        targets = [payer, *(link.managed for link in payer.managed_links if link.managed)]
    elif mode == RenewMode.OTHER:
        if target_id is None:
            raise TargetNotFoundError
        targets = [
            link.managed
            for link in payer.managed_links
            if link.managed is not None and link.managed.id == target_id
        ]
        if not targets:
            raise TargetNotFoundError
    else:
        raise ValueError(f"Unsupported renew mode: {mode}")

    return await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=targets,
        tariff=tariff,
        days=days,
        receiver=receiver,
        fee_percent=fee_percent,
    )
