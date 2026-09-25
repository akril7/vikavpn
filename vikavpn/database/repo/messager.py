from sqlalchemy import select, delete as sql_delete
from sqlalchemy.orm import joinedload

from database.enums import Messenger
from database.models import UserMessenger, User
from database.repo.base import BaseRepository


class MessengerAlreadyBoundError(Exception):
    """Этот messenger-аккаунт уже привязан к другому пользователю."""

    def __init__(self, messenger: Messenger, external_id: int, user_id: int):
        self.messenger = messenger
        self.external_id = external_id
        self.user_id = user_id
        super().__init__(
            f"{messenger}:{external_id} already bound to user {user_id}"
        )


class UserMessengerRepository(BaseRepository[UserMessenger]):
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

    async def get_by_external_with_user(
        self, messenger: Messenger, external_id: int
    ) -> UserMessenger | None:
        stmt = (
            select(UserMessenger)
            .where(
                UserMessenger.messenger == messenger,
                UserMessenger.external_id == external_id,
            )
            .options(joinedload(UserMessenger.user))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[UserMessenger]:
        stmt = (
            select(UserMessenger)
            .where(UserMessenger.user_id == user_id)
            .order_by(UserMessenger.id)
        )
        return list((await self.session.scalars(stmt)).all())

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

    async def get_user_by_external(
        self, messenger: Messenger, external_id: int
    ) -> User | None:
        """Сразу User по его аккаунту в мессенджере (без промежуточного объекта)."""
        stmt = (
            select(User)
            .join(UserMessenger, UserMessenger.user_id == User.id)
            .where(
                UserMessenger.messenger == messenger,
                UserMessenger.external_id == external_id,
            )
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    # ─────────── Проверки ───────────

    async def is_bound(
        self, messenger: Messenger, external_id: int
    ) -> bool:
        return await self.exists(messenger=messenger, external_id=external_id)

    async def is_bound_to_user(
        self, messenger: Messenger, external_id: int, user_id: int
    ) -> bool:
        stmt = select(UserMessenger).where(
            UserMessenger.messenger == messenger,
            UserMessenger.external_id == external_id,
            UserMessenger.user_id == user_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none() is not None

    # ─────────── Привязка (главный метод) ───────────

    async def bind(
        self,
        *,
        user_id: int,
        messenger: Messenger,
        external_id: int,
    ) -> UserMessenger:
        """ Привязать messenger-аккаунт к пользователю """
        existing = await self.get_by_external(messenger, external_id)

        if existing is not None:
            if existing.user_id == user_id:
                return existing
            raise MessengerAlreadyBoundError(
                messenger, external_id, existing.user_id
            )

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
        self, *, user_id: int, messenger: Messenger
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

    async def unbind_by_external(
        self, messenger: Messenger, external_id: int
    ) -> bool:
        stmt = sql_delete(UserMessenger).where(
            UserMessenger.messenger == messenger,
            UserMessenger.external_id == external_id,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        return result.rowcount > 0

    async def unbind_all_for_user(self, user_id: int) -> int:
        stmt = sql_delete(UserMessenger).where(UserMessenger.user_id == user_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        return result.rowcount
