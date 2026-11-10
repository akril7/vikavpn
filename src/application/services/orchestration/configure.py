from loguru import logger

from src.application.ports.services import ConfiguratorError
from src.domain.models import User
from src.application.ports.registry import RegistryLike
from src.application.ports.users_loader import UsersLoader
from src.application.lifecycle.reloader import Reloader


def apply(users: list[User], registry: RegistryLike, names: list[str]):
    for name in names:
        target = registry.get_configurator(name)
        logger.info(f"Применение настроек для {name}")
        try:
            target.apply(users)
        except ConfiguratorError as e:
            logger.warning(str(e))


def build_reloader(
    registry: RegistryLike,
    users_loader: UsersLoader,
    names: list[str],
    debounce: float = 3.0,
    max_delay: float = 30.0,
) -> Reloader:
    async def _apply():
        users = await users_loader()
        apply(users, registry, names)

    return Reloader(_apply, debounce=debounce, max_delay=max_delay)
