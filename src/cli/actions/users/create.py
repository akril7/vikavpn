from sqlalchemy.exc import IntegrityError

from src.application.ports.repo import MessengerAlreadyBoundError
from src.application.users.registration import register_user
from src.cli.async_runtime import runtime
from src.domain.enums import Messenger
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository, UserMessengerRepository


def create_user(ios_user: bool, telegram_id: int | None = None) -> tuple[bool, str]:
    return runtime.run(_create_user(ios_user, telegram_id))


async def _create_user(ios_user: bool, telegram_id: int | None = None) -> tuple[bool, str]:
    async with Session() as session:
        user_repo = UserRepository(session)
        messenger_repo = UserMessengerRepository(session)

        messenger = (Messenger.TELEGRAM, telegram_id) if telegram_id else None

        try:
            user = await register_user(
                user_repo=user_repo,
                messenger_repo=messenger_repo,
                ios_user=ios_user,
                messenger=messenger
            )
        except IntegrityError as exc:
            return False, str(exc)
        except MessengerAlreadyBoundError as exc:
            return False, f"Telegram ID уже привязан: {exc}"

        await session.commit()

    return True, f"Пользователь {user.name} создан (до {user.sub_expires_at})"
