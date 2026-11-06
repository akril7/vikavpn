from loguru import logger

from src.domain.models import User
from src.application.ports.registry import RegistryLike
from src.application.ports.users_loader import UsersLoader
from src.application.lifecycle.reloader import Reloader


def apply(users: list[User], registry: RegistryLike, by_names: list[str] | None = None):
    for name, target in registry.get_configure_targets(by_names).items():
        logger.info(f"Применение настроек для {name}")
        target.apply(users)


async def apply_active_users(
    registry: RegistryLike,
    users_loader: UsersLoader,
    by_names: list[str] | None = None,
) -> None:
    """Загружает активных пользователей и применяет их к endpoints."""

    users = await users_loader()
    apply(users, registry, by_names=by_names)


def build_reloader(
    registry: RegistryLike,
    users_loader: UsersLoader,
    by_names: list[str] | None = None,
    debounce: float = 3.0,
    max_delay: float = 30.0,
) -> Reloader:
    """Создаёт Reloader, привязанный к apply_active_users."""
    async def _apply() -> None:
        await apply_active_users(registry, users_loader, by_names)

    return Reloader(_apply, debounce=debounce, max_delay=max_delay)
