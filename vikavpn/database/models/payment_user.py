from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class PaymentUser(Base):
    __tablename__ = "payment_users"

    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
