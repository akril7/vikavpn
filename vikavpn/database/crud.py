from datetime import datetime, timedelta, time, UTC
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
    UserManagement, Messenger, UserMessenger
)


class UserNotFoundError(Exception):
    """Пользователь не найден."""


class MessengerAlreadyBoundError(Exception):
    """Этот messenger-аккаунт уже привязан к другому пользователю."""


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


async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> User | None:
    stmt = (
        select(User)
        .where(User.uuid == uuid)
    )
    return await session.scalar(stmt)


async def get_user_with_managed(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.managed_links).selectinload(UserManagement.managed))
    )
    return await session.scalar(stmt)


async def get_user_by_messenger(
    session: AsyncSession,
    messenger: Messenger,
    external_id: int,
) -> User | None:
    stmt = (
        select(User)
        .join(UserMessenger, UserMessenger.user_id == User.id)
        .where(
            UserMessenger.messenger == messenger,
            UserMessenger.external_id == external_id,
        )
        .options(selectinload(User.managed_links))
    )
    return await session.scalar(stmt)


async def get_user_by_name(session: AsyncSession, name: str) -> User | None:
    stmt = (
        select(User)
        .where(User.name == name)
        .options(selectinload(User.managed_links))
    )
    return (await session.scalars(stmt)).first()


async def get_active_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).where(
        User.sub_expires_at > datetime.now(UTC),
    )
    return (await session.scalars(stmt)).all()


async def get_expired_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).where(
        User.sub_expires_at <= datetime.now(UTC),
    ).options(selectinload(User.messenger_links))
    return (await session.scalars(stmt)).all()


async def get_users_expiring_tomorrow(
    session: AsyncSession,
) -> Sequence[User]:
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
    start = datetime.combine(tomorrow, time.min)
    end = start + timedelta(days=1)

    stmt = (
        select(User)
        .where(
            User.sub_expires_at >= start,
            User.sub_expires_at < end,
        )
        .options(selectinload(User.messenger_links))
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
    await session.commit()

    return obj


async def create_payment_user(
        session: AsyncSession,
        payment_id: int,
        user_id: int,
) -> PaymentUser:
    obj = PaymentUser(payment_id=payment_id, user_id=user_id)
    session.add(obj)
    await session.commit()

    return obj


async def get_payment_by_label(
        session: AsyncSession, label: str
) -> Payment | None:
    stmt = select(Payment).where(Payment.label == label)
    return await session.scalar(stmt)


async def get_payment_user_ids(
        session: AsyncSession, payment_id: int
) -> list[int]:
    stmt = select(PaymentUser.user_id).where(PaymentUser.payment_id == payment_id)
    return list((await session.scalars(stmt)).all())


async def bind_messenger(
    session: AsyncSession,
    user: User,
    messenger: Messenger,
    external_id: int,
) -> UserMessenger:
    existing = await session.scalar(
        select(UserMessenger).where(
            UserMessenger.messenger == messenger,
            UserMessenger.external_id == external_id,
        )
    )
    if existing is not None:
        if existing.user_id == user.id:
            return existing
        raise MessengerAlreadyBoundError(
            f"{messenger}:{external_id} already bound to user {existing.user_id}"
        )

    obj = UserMessenger(
        user_id=user.id,
        messenger=messenger,
        external_id=external_id,
    )
    session.add(obj)
    await session.commit()
    return obj
