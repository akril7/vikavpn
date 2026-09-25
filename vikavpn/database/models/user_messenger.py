from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum, UniqueConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.enums import Messenger, enum_values
from database.models.base import Base, IdMixin


if TYPE_CHECKING:
    from database.models.user import User


class UserMessenger(IdMixin, Base):
    __tablename__ = "user_messengers"
    __table_args__ = (
        UniqueConstraint("messenger", "external_id", name="uq_messenger_external"),
        UniqueConstraint("user_id", "messenger", name="uq_user_messenger")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    messenger: Mapped[Messenger] = mapped_column(
        Enum(Messenger, values_callable=enum_values),
        index=True,
    )
    external_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True
    )

    user: Mapped["User"] = relationship(
        back_populates="messenger_links"
    )

    def __repr__(self) -> str:
        return (
            f"UserMessenger({self.user_id=}, "
            f"{self.messenger=}, {self.external_id=})"
        )
