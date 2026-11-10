from src.cli.actions.users.utils import find_user
from src.cli.async_runtime import runtime
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository


def delete_user(name_or_uuid: str) -> tuple[bool, str]:
    return runtime.run(_delete_user(name_or_uuid))


async def _delete_user(name_or_uuid: str) -> tuple[bool, str]:
    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        name = user.name
        await repo.delete(user)
        await session.commit()
        return True, f"Пользователь {name} удалён"
