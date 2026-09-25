from database.connection import Session
from database.enums import Messenger
from database.models import User
from database.repo.user import UserRepository


async def load_user(telegram_id: int) -> User | None:
    async with Session() as session:
        repo = UserRepository(session)
        return await repo.get_by_messenger(
            Messenger.TELEGRAM, telegram_id
        )


async def load_user_with_managed(telegram_id: int) -> User | None:
    async with Session() as session:
        repo = UserRepository(session)

        user = await repo.get_by_messenger(
            Messenger.TELEGRAM, telegram_id
        )

        return await repo.get_with_managed_users(user.id) if user else None


def managed_targets(user: User) -> list[tuple[int, str]]:
    return [
        (link.managed.id, link.managed.name)
        for link in user.managed_links
        if link.managed is not None
    ]
