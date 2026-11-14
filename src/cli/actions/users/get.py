from src.application.users.profile import ProfileView, build_profile
from src.configuration import Settings
from src.domain.models import User
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository
from src.cli.async_runtime import runtime
from src.infrastructure.persistence.repo.options import full_options

from .utils import find_user


def list_users(load_options: bool = False) -> list[User]:
    """ Возвращает список всех пользователей """
    return runtime.run(_list_users(load_options=load_options))


async def _list_users(load_options: bool = False) -> list[User]:
    async with Session() as session:
        repo = UserRepository(session)
        return await repo.all(options=full_options() if load_options else None)


def get_user(name_or_uuid: str) -> User | None:
    return runtime.run(_get_user(name_or_uuid))


async def _get_user(name_or_uuid: str) -> User | None:
    async with Session() as session:
        repo = UserRepository(session)

        user = await find_user(repo, name_or_uuid)
        if user is None:
            return None

        return user


def get_user_profile(name_or_uuid: str, settings: Settings) -> ProfileView | None:
    user = get_user(name_or_uuid)
    if user is None:
        return None

    return build_profile(user, settings)
