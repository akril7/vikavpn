from typing import Protocol

from src.domain.enums import Messenger
from src.domain.models import UserMessenger


class MessengerAlreadyBoundError(Exception):
    """Этот messenger-аккаунт уже привязан к другому пользователю."""

    def __init__(self, messenger: Messenger, external_id: int, user_id: int):
        self.messenger = messenger
        self.external_id = external_id
        self.user_id = user_id
        super().__init__(
            f"{messenger}:{external_id} already bound to user {user_id}"
        )


class UserMessengerRepoLike(Protocol):
    async def bind(
        self,
        user_id: int,
        messenger: Messenger,
        external_id: int,
    ) -> UserMessenger:
        """ Привязать messenger-аккаунт к пользователю """
        ...

    # ─────────── Отвязка ───────────

    async def unbind(
        self, user_id: int, messenger: Messenger
    ) -> bool:
        """Отвязать аккаунт мессенджера от пользователя.

        Возвращает True, если связь была удалена.
        """
        ...
