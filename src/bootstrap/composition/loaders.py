from src.application.manager import configure
from src.application.ports.registry import RegistryLike
from src.infrastructure.persistence.loaders import load_active_users


async def apply_active_users(registry: RegistryLike, names: list[str] | None = None) -> None:
    await configure.apply_active_users(registry, load_active_users, names)
