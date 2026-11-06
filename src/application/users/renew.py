from enum import StrEnum

from src.application.payment.lifecycle import create_payment
from src.application.ports.repo import PaymentRepoLike, PaymentUserRepoLike
from src.domain.enums import Tariff
from src.domain.models import Payment, User


class RenewError(Exception):
    """Базовая ошибка продления с сообщением для пользователя.

    Attributes:
        message: Текст, который можно показать пользователю в UI
            (например, через ``call.answer(..., show_alert=True)``).
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


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
    payment_repo: PaymentRepoLike,
    link_repo: PaymentUserRepoLike,
    payer: User,
    mode: RenewMode,
    tariff: Tariff,
    days: int,
    fee_percent: float = 0,
    target_id: int | None = None
) -> Payment:
    """
    Создать платёж для продления подписки. Требует загруженных payer.managed

    Определяет цели продления по режиму (``mode``), создаёт платёж
    с рассчитанной суммой и возвращает его вместе с URL для оплаты.
    Сумма рассчитывается как ``plan.price * len(targets)`` с учётом
    ``fee_percent``.

    Запись платежа добавляется в сессию через ``flush``, но **не
    коммитится** — коммит выполняет вызывающий код.

    Raises:
        TargetNotFoundError: Для ``RenewMode.OTHER`` не передан
            ``target_id`` или он не соответствует ни одному
            управляемому пользователю.
        ValueError: Неизвестный режим продления или тариф/срок
            не соответствует ни одному из ``PLANS``.
    """
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
        fee_percent=fee_percent,
    )
