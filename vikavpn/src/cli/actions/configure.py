from loguru import logger

from src.cli.async_runtime import runtime
from src.core.interfaces import ServiceError
from src.core.lifecycle.notify import notify_reload
from src.infrastructure.manager import configure as configure_manager
from src.infrastructure.manager import control
from src.infrastructure.manager.registry import Registry
from src.infrastructure.system.subprocess import is_root
from src.cli.console import console, err, ok, warn
from src.cli.utils.editor import edit_env
from src.settings import Settings


def apply(registry: Registry, names: list[str] | None = None) -> bool:
    """Применить конфигурацию (все или выбранные)."""
    try:
        with console.status("[cyan]Применяю конфигурацию…[/]"):
            runtime.run(configure_manager.apply_active_users(registry, names))
        ok("Конфигурация применена")
        return True
    except ServiceError as exc:
        err(f"Ошибка применения: {exc}")
        return False
    except Exception as exc:  # noqa: BLE001
        logger.exception("apply failed")
        err(f"Ошибка применения: {exc}")
        return False


def restart_all(registry: Registry) -> bool:
    """Перезапустить все control-таргеты."""
    if not is_root():
        err("Требуются права root для перезапуска сервисов.")
        warn("Запустите панель через sudo.")
        return False

    targets = list(registry.get_control_targets().keys())
    ok_all = True
    for name in targets:
        with console.status(f"[cyan]Перезапускаю {name}…[/]"):
            try:
                control.restart(registry, [name])
                ok(f"{name}: перезапущен")
            except ServiceError as exc:
                err(f"{name}: {exc}")
                ok_all = False
            except Exception as exc:  # noqa: BLE001
                logger.exception(f"restart failed for {name}")
                err(f"{name}: {exc}")
                ok_all = False
    return ok_all


def open_env_and_maybe_restart() -> tuple[bool, bool]:
    """Открывает .env. Возвращает (было_открыто, надо_перезагрузить_сервисы).

    Сам перезапуск делает вызывающий код (меню), потому что ему нужно
    знать про ctx.reload().
    """
    opened = edit_env()
    return opened, opened


def trigger_reload(settings: Settings) -> None:
    """Сообщить reloader'у, что надо переприменить конфиги."""
    async def _go():
        await notify_reload(settings.reloader.url, timeout=settings.payments.reload_timeout)
    try:
        runtime.run(_go())
    except Exception:
        logger.exception("notify_reload failed")
