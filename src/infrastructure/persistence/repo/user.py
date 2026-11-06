from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Load

from src.application.ports.repo import UserRepoLike
from src.domain.utils.dt import utcnow
from src.domain.enums import Messenger
from src.domain.models import User, UserMessenger
from src.infrastructure.persistence.repo.base import BaseRepository


class UserRepository(UserRepoLike, BaseRepository[User]):
    model = User

    # ─────────── Поиск по уникальным полям ───────────
    async def get_with(
            self,
            pk: int,
            *,
            options: tuple[Load, ...] = ()
    ) -> User | None:
        """Поиск по pk."""
        stmt = select(User).where(User.id == pk).options(*options)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
        *,
        options: tuple[Load, ...] = (),
    ) -> User | None:
        """Поиск по имени."""
        stmt = select(User).where(User.name == name).options(*options)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_uuid(
        self,
        uuid: UUID,
        *,
        options: tuple[Load, ...] = (),
    ) -> User | None:
        """Поиск по UUID."""
        stmt = select(User).where(User.uuid == uuid).options(*options)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Поиск по messenger-аккаунту ───────────

    async def get_by_messenger(
        self,
        messenger: Messenger,
        external_id: int,
        *,
        options: tuple[Load, ...] = (),
    ) -> User | None:
        """Поиск по id в мессенджере."""
        stmt = (
            select(User)
            .join(User.messenger_links)
            .where(
                UserMessenger.messenger == messenger,
                UserMessenger.external_id == external_id,
            )
            .options(*options)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_telegram_id(
        self,
        telegram_id: int,
        *,
        options: tuple[Load, ...] = (),
    ) -> User | None:
        return await self.get_by_messenger(
            Messenger.TELEGRAM, telegram_id, options=options,
        )

    # ─────────── Списки с фильтрацией ───────────

    async def list_expiring_within(
        self,
        hours: int = 24,
        *,
        options: tuple[Load, ...] = (),
    ) -> list[User]:
        now = utcnow()
        stmt = (
            select(User)
            .where(
                User.sub_expires_at >= now,
                User.sub_expires_at < (now + timedelta(hours=hours)),
            )
            .order_by(User.sub_expires_at)
            .options(*options)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_active(
        self,
        limit: int | None = None,
        offset: int = 0,
        *,
        options: tuple[Load, ...] = (),
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.sub_expires_at > utcnow())
            .order_by(User.id)
            .limit(limit)
            .offset(offset)
            .options(*options)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_expired(
        self,
        limit: int | None = None,
        offset: int = 0,
        *,
        options: tuple[Load, ...] = (),
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.sub_expires_at <= utcnow())
            .order_by(User.sub_expires_at)
            .limit(limit)
            .offset(offset)
            .options(*options)
        )
        return list((await self.session.scalars(stmt)).all())

    # ─────────── Специфичные операции ───────────

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists(name=name)

    async def exists_by_uuid(self, uuid: UUID) -> bool:
        return await self.exists(uuid=uuid)

    async def get_next_expire_at(self) -> datetime | None:
        """Ближайшая дата окончания подписки среди активных (строго > now)."""
        stmt = (
            select(func.min(User.sub_expires_at))
            .where(User.sub_expires_at > utcnow())
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()
