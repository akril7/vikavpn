from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.enums import Messenger, Tariff
from database.models import User, UserMessenger, UserManagement
from database.repo.base import BaseRepository
from utils.datetime import utcnow


def extend_subscription(user: User, tariff: Tariff, days: int):
    now = utcnow()
    base = user.sub_expires_at if user.sub_expires_at > now else now
    user.sub_expires_at = base + timedelta(days=days)
    user.proxy_user = True
    user.vpn_user = tariff == Tariff.FULL


class UserRepository(BaseRepository[User]):
    model = User

    # ─────────── Поиск по уникальным полям ───────────

    async def get_by_name(self, name: str) -> User | None:
        stmt = select(User).where(User.name == name)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        stmt = select(User).where(User.uuid == uuid)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Поиск по messenger-аккаунту ───────────

    async def get_by_messenger(
        self, messenger: Messenger, external_id: int
    ) -> User | None:
        """Найти user по его аккаунту в мессенджере."""
        stmt = (
            select(User)
            .join(User.messenger_links)
            .where(
                UserMessenger.messenger == messenger,
                UserMessenger.external_id == external_id,
            )
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.get_by_messenger(Messenger.TELEGRAM, telegram_id)

    async def get_by_vk_id(self, vk_id: int) -> User | None:
        return await self.get_by_messenger(Messenger.VK, vk_id)

    # ─────────── Получить вместе с ───────────

    async def get_with_messengers(self, user_id: int) -> User | None:
        """User + все его messenger-аккаунты (для .telegram_id / .vk_id)."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.messenger_links))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_with_payments(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.payments))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_with_managed_users(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.managed_links).joinedload(UserManagement.managed)
            )
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Списки с фильтрацией ───────────

    async def list_expiring_within(self, hours: int = 24, load_messengers: bool = True) -> list[User]:
        now = utcnow()
        stmt = (
            select(User)
            .where(
                User.sub_expires_at >= now,
                User.sub_expires_at < now + timedelta(hours=hours),
            )
            .order_by(User.sub_expires_at)
        )
        if load_messengers:
            stmt.options(selectinload(User.messenger_links))

        return list((await self.session.scalars(stmt)).all())

    async def list_active(
        self, limit: int = 100, offset: int = 0
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.sub_expires_at > utcnow())
            .order_by(User.id)
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_expired(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = (
            select(User)
            .where(User.sub_expires_at <= utcnow())
            .order_by(User.sub_expires_at)
            .limit(limit)
            .offset(offset)
        )
        return list((await self.session.scalars(stmt)).all())

    async def list_by_flag(
        self,
        *,
        vpn_user: bool | None = None,
        proxy_user: bool | None = None,
        ios_user: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        stmt = select(User)
        if vpn_user is not None:
            stmt = stmt.where(User.vpn_user == vpn_user)
        if proxy_user is not None:
            stmt = stmt.where(User.proxy_user == proxy_user)
        if ios_user is not None:
            stmt = stmt.where(User.ios_user == ios_user)
        stmt = stmt.order_by(User.id).limit(limit).offset(offset)
        return list((await self.session.scalars(stmt)).all())

    # ─────────── Специфичные операции ───────────

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists(name=name)

    async def exists_by_uuid(self, uuid: UUID) -> bool:
        return await self.exists(uuid=uuid)
