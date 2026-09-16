from uuid import UUID, uuid4
from datetime import datetime
from typing import Iterable

from sqlalchemy import String, Uuid, DateTime, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    enabled: Mapped[bool] = mapped_column(default=True)

    messager: Mapped["UserMessager"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    managed_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.manager_id",
        back_populates="manager",
        cascade="all, delete-orphan"
    )

    manager_links: Mapped[list["UserManagement"]] = relationship(
        foreign_keys="UserManagement.managed_id",
        back_populates="managed",
        cascade="all, delete-orphan"
    )

    managed_users: AssociationProxy[list["User"]] = association_proxy(
        "managed_links", "managed",
    )
    managers: AssociationProxy[list["User"]] = association_proxy(
        "manager_links", "manager",
    )

    def __repr__(self):
        return f"User({self.id=}, {self.name=})"


class UserMessager(Base):
    __tablename__ = "user_messagers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True, index=True)
    vk_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True, index=True)

    user: Mapped["User"] = relationship(
        back_populates="messager",
        uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"UserMessenger({self.id=}, {self.user_id=}, {self.telegram_id=}, {self.vk_id=})"
        )


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


Users = Iterable[User]
