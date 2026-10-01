from loguru import logger

from src.db.models import Users
from src.db.connection import Session
from src.db.repo import UserRepository
from src.core.reload import Reloader

from .registry import Registry


def apply(users: Users, registry: Registry, by_names: list[str] | None = None):
    for name, target in registry.get_configure_targets(by_names).items():
        logger.info(f"Применение настроек для {name}")
        target.apply(users)


async def apply_active_users(
    registry: Registry,
    by_names: list[str] | None = None,
) -> None:
    """Загружает активных пользователей и применяет их к endpoints."""
    async with Session() as session:
        repo = UserRepository(session)
        users = await repo.list_active(limit=None)

    apply(users, registry, by_names=by_names)


def build_reloader(
    registry: Registry,
    by_names: list[str] | None = None,
    debounce: float = 3.0,
    max_delay: float = 30.0,
) -> Reloader:
    """Создаёт Reloader, привязанный к apply_active_users."""
    async def _apply() -> None:
        await apply_active_users(registry, by_names)

    return Reloader(_apply, debounce=debounce, max_delay=max_delay)
