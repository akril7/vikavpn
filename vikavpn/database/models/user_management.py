from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from database.models.user import User


class UserManagement(Base):
    """Связь «manager управляет managed»."""

    __tablename__ = "user_managements"
    __table_args__ = (
        CheckConstraint("manager_id != managed_id", name="ck_no_self_management"),
    )

    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    managed_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    manager: Mapped["User"] = relationship(
        foreign_keys=[manager_id],
        back_populates="managed_links",
    )
    managed: Mapped["User"] = relationship(
        foreign_keys=[managed_id],
        back_populates="manager_links",
    )

    def __repr__(self) -> str:
        return f"UserManagement({self.manager_id=}, {self.managed_id=})"
