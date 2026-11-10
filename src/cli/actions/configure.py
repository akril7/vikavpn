from loguru import logger

from src.application.ports.services import ServiceError
from src.bootstrap.composition.loaders import apply_active_users
from src.bootstrap.registry import Registry
from src.infrastructure.apps.reloader.notify import notify_reload
from src.cli.async_runtime import runtime
from src.cli.console import console, err, ok, warn
from src.configuration import Settings


def apply(registry: Registry, names: list[str]) -> bool:
    """Применить конфигурацию (все или выбранные)."""

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
        with console.status(f"[cyan]Применяю конфигурацию для {name}...[/]"):
            try:
                runtime.run(apply_active_users(registry, [name]))
                ok(f"{name}: конфигурация применена")
            except ServiceError as exc:
                err(f"{name}: {exc}")
                ok_all = False
            except Exception as exc:  # noqa: BLE001
                logger.exception(f"install failed for {name}")
                err(f"{name}: {exc}")
                ok_all = False
    return ok_all


def trigger_reload(settings: Settings) -> None:
    """Сообщить reloader'у, что надо переприменить конфиги."""
    async def _go():
        await notify_reload(settings.reloader.url, timeout=settings.payments.reload_timeout)

    try:
        runtime.run(_go())
    except Exception:
        logger.exception("notify_reload failed")
