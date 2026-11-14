from src.application.services.orchestration import configure
from src.application.ports.registry import RegistryLike
from src.infrastructure.persistence.loaders import load_active_users


async def apply_active_users(registry: RegistryLike, names: list[str]) -> None:
    configure.apply(await load_active_users(), registry, names)
