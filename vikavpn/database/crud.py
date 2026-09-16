from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.app import TZ
from .models import User, UserMessager, UserManagement


def create_user(
        session: Session,
        name: str,
        password: str,
        sub_expires_at: datetime,
        uuid: UUID | None = None,
        vpn_user: bool = True,
        proxy_user: bool = True,
        ios_user: bool = False,
        enabled: bool = True) -> User:
    obj = User(
        name=name,
        password=password,
        sub_expires_at=sub_expires_at,
        vpn_user=vpn_user,
        proxy_user=proxy_user,
        ios_user=ios_user,
        enabled=enabled
    )
    if uuid:
        obj.uuid = uuid

    session.add(obj)
    session.commit()

    return obj


def get_users_by_names(session: Session, names: list[str]) -> Sequence[User]:
    stmt = select(User).where(User.name.in_(names))
    return session.scalars(stmt).all()


def get_user_by_name(session: Session, name: str) -> User:
    return get_users_by_names(session, [name])[0]


def get_active_users(session: Session) -> Sequence[User]:
    stmt = select(User).where(User.enabled.is_(True),
                              User.sub_expires_at > datetime.now(tz=TZ))
    return session.scalars(stmt).all()


def create_user_messager(
        session: Session,
        user: User,
        telegram_id: int | None,
        vk_id: int | None) -> UserMessager:
    obj = UserMessager(
        user_id=user.id,
        telegram_id=telegram_id,
        vk_id=vk_id
    )

    session.add(obj)
    session.commit()

    return obj


def create_user_management(
        session: Session,
        manager: User,
        managed: User) -> UserManagement:
    obj = UserManagement(
        manager_id=manager.id,
        managed_id=managed.id
    )

    session.add(obj)
    session.commit()

    return obj
