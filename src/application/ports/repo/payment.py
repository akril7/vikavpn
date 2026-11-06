from decimal import Decimal
from typing import Protocol

from src.domain.enums import Tariff
from src.domain.models import Payment


class PaymentRepoLike(Protocol):
    async def create_payment(
        self,
        payer_id: int,
        tariff: Tariff,
        days: int,
        amount: Decimal,
        label: str | None = None,
    ) -> Payment:
        ...

    async def get_by_label(self, label: str) -> Payment | None:
        ...

    async def mark_paid_if_pending(
            self,
            label: str,
            amount: Decimal,
    ) -> Payment | None:
        """Атомарно пометить платёж оплаченным, если он ещё ``PENDING``. """
        ...
