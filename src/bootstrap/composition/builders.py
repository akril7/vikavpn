from src.application.lifecycle.reloader import Reloader
from src.application.lifecycle.expiryscheduler import ExpiryScheduler
from src.application.services.orchestration import configure
from src.application.services.orchestration.installation import filter_installed_names
from src.bootstrap.registry import Registry
from src.configuration.aggregator import Settings
from src.infrastructure.persistence.loaders import load_active_users, load_next_expire_at


def build_reloader_subsystem(settings: Settings) -> tuple[Registry, Reloader, ExpiryScheduler]:
    registry = Registry(settings)
    reloader = configure.build_reloader(
        registry,
        users_loader=load_active_users,
        names=filter_installed_names(registry, registry.names_of_configurators),
        debounce=settings.reloader.debounce,
        max_delay=settings.reloader.max_delay,
    )
    expiry = ExpiryScheduler(reloader, next_expire_at=load_next_expire_at)
    return registry, reloader, expiry
