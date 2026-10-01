from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime

from src.db.enums import Tariff, enum_values, PaymentStatus
from src.db.models.base import Base, CreateAtMixin, IdMixin


if TYPE_CHECKING:
    pass


class Payment(IdMixin, CreateAtMixin, Base):
    __tablename__ = "payments"

    payer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    label: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    days: Mapped[int] = mapped_column()
    tariff: Mapped[Tariff] = mapped_column(
        Enum(Tariff, values_callable=enum_values)
    )

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=enum_values),
        default=PaymentStatus.PENDING,
    )
    paid_at: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)

    users: Mapped[list["User"]] = relationship(
        secondary="payment_users",
        back_populates="payments",
        passive_deletes=True,
    )
