from uuid import UUID, uuid4
from datetime import datetime
from enum import StrEnum
from typing import Iterable

from sqlalchemy import (
    String,
    Uuid,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum,
)
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config.app import TZ


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(50))
    sub_expires_at: Mapped[datetime] = mapped_column(DateTime)
    uuid: Mapped[UUID] = mapped_column(Uuid, default=uuid4, unique=True, index=True)
    vpn_user: Mapped[bool] = mapped_column(default=True)
    proxy_user: Mapped[bool] = mapped_column(default=True)
    ios_user: Mapped[bool] = mapped_column(default=False)

    managed_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.manager_id",
        back_populates="manager",
        cascade="all, delete-orphan",
    )

    manager_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.managed_id",
        back_populates="managed",
        cascade="all, delete-orphan",
    )

    managed_users: AssociationProxy[list["User"]] = association_proxy(
        "managed_links",
        "managed",
    )
    managers: AssociationProxy[list["User"]] = association_proxy(
        "manager_links",
        "manager",
    )

    @property
    def is_active(self):
        return self.sub_expires_at > datetime.now()

    def __repr__(self):
        return f"User({self.id=}, {self.name=})"


class UserManagement(Base):
    """Связь «manager управляет managed»."""

    __tablename__ = "user_managements"
    __table_args__ = (
        UniqueConstraint("manager_id", "managed_id", name="uq_user_management_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    manager_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    managed_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
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


class Tariff(StrEnum):
    PROXY = "proxy"
    FULL = "full"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    payer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    operation_id: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    label: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True
    )
    amount: Mapped[int] = mapped_column()
    tariff: Mapped[Tariff] = mapped_column(
        Enum(Tariff, values_callable=_enum_values)
    )
    days: Mapped[int] = mapped_column()
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=_enum_values),
        default=PaymentStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(tz=TZ)
    )
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)


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


Users = Iterable[User]
