from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utc import UtcDateTime
from uuid import UUID, uuid4

from src.core.utils.dt import utcnow
from .base import IdMixin, Base
from ..enums import Messenger


class User(IdMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, default=uuid4, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(32))
    sub_expires_at: Mapped[datetime] = mapped_column(UtcDateTime, default=utcnow)
    vpn_user: Mapped[bool] = mapped_column(default=True)
    proxy_user: Mapped[bool] = mapped_column(default=True)
    ios_user: Mapped[bool] = mapped_column(default=False)

    managed_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.manager_id",
        back_populates="manager",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    manager_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.managed_id",
        back_populates="managed",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    messenger_links: Mapped[list["UserMessenger"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    payments: Mapped[list["Payment"]] = relationship(
        secondary="payment_users",
        back_populates="users",
        passive_deletes=True,
    )

    @property
    def is_active(self) -> bool:
        return self.sub_expires_at > utcnow()

    @property
    def telegram_id(self) -> int | None:
        for link in self.messenger_links:
            if link.messenger == Messenger.TELEGRAM:
                return link.external_id
        return None

    @property
    def vk_id(self) -> int | None:
        for link in self.messenger_links:
            if link.messenger == Messenger.VK:
                return link.external_id
        return None

    def __repr__(self):
        return f"User({self.id=}, {self.name=})"
