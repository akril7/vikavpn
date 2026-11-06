from sqlalchemy import select, delete as sql_delete

from src.domain.enums import Messenger
from src.domain.models import UserMessenger
from src.application.ports.repo import MessengerAlreadyBoundError, UserMessengerRepoLike
from src.infrastructure.persistence.repo.base import BaseRepository


class UserMessengerRepository(UserMessengerRepoLike, BaseRepository[UserMessenger]):
    model = UserMessenger

    # ─────────── Поиск ───────────

    async def get_by_external(
        self, messenger: Messenger, external_id: int
    ) -> UserMessenger | None:
        stmt = select(UserMessenger).where(
            UserMessenger.messenger == messenger,
            UserMessenger.external_id == external_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_user_and_messenger(
        self, user_id: int, messenger: Messenger
    ) -> UserMessenger | None:
        """Аккаунт конкретного пользователя в конкретном мессенджере.

        Полезно, если есть UniqueConstraint(user_id, messenger).
        """
        stmt = select(UserMessenger).where(
            UserMessenger.user_id == user_id,
            UserMessenger.messenger == messenger,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Привязка (главный метод) ───────────

    async def bind(
        self,
        user_id: int,
        messenger: Messenger,
        external_id: int,
    ) -> UserMessenger:
        """ Привязать messenger-аккаунт к пользователю """
        existing = await self.get_by_external(messenger, external_id)
        if existing is not None:
            if existing.user_id == user_id:
                return existing
            raise MessengerAlreadyBoundError(messenger, external_id, existing.user_id)

        by_user = await self.get_by_user_and_messenger(user_id, messenger)
        if by_user is not None:
            by_user.external_id = external_id
            await self.session.flush()
            return by_user

        obj = UserMessenger(
            user_id=user_id,
            messenger=messenger,
            external_id=external_id,
        )
        self.session.add(obj)
        await self.session.flush()

        return obj

    # ─────────── Отвязка ───────────

    async def unbind(
        self, user_id: int, messenger: Messenger
    ) -> bool:
        """Отвязать аккаунт мессенджера от пользователя.

        Возвращает True, если связь была удалена.
        """
        stmt = sql_delete(UserMessenger).where(
            UserMessenger.user_id == user_id,
            UserMessenger.messenger == messenger,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        return result.rowcount > 0
