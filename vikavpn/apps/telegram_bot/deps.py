from database.connection import Session
from database.crud import get_user_by_messenger, get_user_with_managed
from database.models import Messenger, User


async def load_user(telegram_id: int) -> User | None:
    async with Session() as session:
        return await get_user_by_messenger(
            session, Messenger.TELEGRAM, telegram_id
        )


async def load_user_with_managed(telegram_id: int) -> User | None:
    async with Session() as session:
        user = await get_user_by_messenger(
            session, Messenger.TELEGRAM, telegram_id
        )
        if user is None:
            return None
        return await get_user_with_managed(session, user.id)


def managed_targets(user: User) -> list[tuple[int, str]]:
    return [(u.id, u.name) for u in user.managed_users]
