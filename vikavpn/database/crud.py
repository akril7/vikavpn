from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    Payment,
    PaymentUser,
    Tariff,
    User,
    UserManagement
)


class UserNotFoundError(Exception):
    """Пользователь не найден."""


async def create_user(
        session: AsyncSession,
        name: str,
        password: str,
        sub_expires_at: datetime,
        uuid: UUID | None = None,
        vpn_user: bool = True,
        proxy_user: bool = True,
        ios_user: bool = False,
) -> User:
    obj = User(
        name=name,
        password=password,
        sub_expires_at=sub_expires_at,
        vpn_user=vpn_user,
        proxy_user=proxy_user,
        ios_user=ios_user,
    )
    if uuid:
        obj.uuid = uuid

    session.add(obj)
    await session.commit()

    return obj


async def get_users_by_names(session: AsyncSession, names: list[str]) -> Sequence[User]:
    stmt = (
        select(User)
        .where(User.name.in_(names))
        .options(selectinload(User.managed_links))
    )

    return (await session.scalars(stmt)).all()


async def get_user_by_name(session: AsyncSession, name: str) -> User:
    users = await get_users_by_names(session, [name])
    if not users:
        raise UserNotFoundError(f"Пользователь '{name}' не найден")
    return users[0]


async def get_active_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).where(
        User.sub_expires_at > datetime.now(),
    )
    return (await session.scalars(stmt)).all()


async def create_user_management(
        session: AsyncSession,
        manager: User,
        managed: User,
) -> UserManagement:
    obj = UserManagement(
        manager_id=manager.id,
        managed_id=managed.id,
    )
    session.add(obj)
    await session.commit()
    return obj


async def create_payment(
        session: AsyncSession,
        payer_id: int,
        tariff: Tariff,
        days: int,
        amount: int,
) -> Payment:
    obj = Payment(
        payer_id=payer_id,
        tariff=tariff,
        days=days,
        amount=amount,
    )
    session.add(obj)
    return obj


async def create_payment_user(
        session: AsyncSession,
        payment_id: int,
        user_id: int,
) -> PaymentUser:
    obj = PaymentUser(payment_id=payment_id, user_id=user_id)
    session.add(obj)
    return obj


async def get_payment_by_label(
        session: AsyncSession, label: str
) -> Payment | None:
    stmt = select(Payment).where(Payment.label == label)
    return await session.scalar(stmt)


async def get_payment_by_operation_id(
        session: AsyncSession, operation_id: str
) -> Payment | None:
    stmt = select(Payment).where(Payment.operation_id == operation_id)
    return await session.scalar(stmt)


async def get_payment_user_ids(
        session: AsyncSession, payment_id: int
) -> list[int]:
    stmt = select(PaymentUser.user_id).where(PaymentUser.payment_id == payment_id)
    return list((await session.scalars(stmt)).all())


async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> User | None:
    stmt = (
        select(User)
        .where(User.uuid == uuid)
    )
    return await session.scalar(stmt)


async def get_managed_users(session: AsyncSession, user_id: int) -> list[User]:
    stmt = (
        select(User)
        .join(UserManagement, UserManagement.managed_id == User.id)
        .where(UserManagement.manager_id == user_id)
    )
    return list((await session.scalars(stmt)).all())
