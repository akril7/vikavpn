from src.application.ports.repo import MessengerAlreadyBoundError
from src.cli.actions.users.utils import find_user
from src.cli.async_runtime import runtime
from src.domain.enums import Messenger
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository, UserMessengerRepository


def unbind_messenger(name_or_uuid: str, messenger_value: str) -> tuple[bool, str]:
    return runtime.run(_unbind_messenger(name_or_uuid, messenger_value))


async def _unbind_messenger(name_or_uuid: str, messenger_value: str) -> tuple[bool, str]:
    try:
        messenger = Messenger(messenger_value)
    except ValueError:
        return False, f"Неизвестный мессенджер: {messenger_value}"

    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        bound = await UserMessengerRepository(session).unbind(
            user_id=user.id, messenger=messenger,
        )
        await session.commit()
        if bound:
            return True, f"{user.name}: {messenger.value} отвязан"
        return False, f"{user.name}: {messenger.value} и так не привязан"


def bind_messenger(
        name_or_uuid: str, messenger_value: str, external_id: int,
) -> tuple[bool, str]:
    return runtime.run(_bind_messenger(name_or_uuid, messenger_value, external_id))


async def _bind_messenger(
        name_or_uuid: str, messenger_value: str, external_id: int,
) -> tuple[bool, str]:
    try:
        messenger = Messenger(messenger_value)
    except ValueError:
        return False, f"Неизвестный мессенджер: {messenger_value}"

    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        try:
            await UserMessengerRepository(session).bind(
                user_id=user.id,
                messenger=messenger,
                external_id=external_id,
            )
        except MessengerAlreadyBoundError as exc:
            return False, str(exc)

        await session.commit()
        return True, f"{user.name}: {messenger.value} → {external_id}"
