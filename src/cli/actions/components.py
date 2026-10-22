from loguru import logger

from src.cli.async_runtime import runtime
from src.core.interfaces import ServiceError
from src.infrastructure.manager import installation
from src.infrastructure.manager.registry import Registry
from src.infrastructure.system.subprocess import is_root
from src.cli.console import console, err, ok, warn


def _require_root(action: str) -> bool:
    if is_root():
        return True
    err(f"Требуются права root для операции «{action}».")
    warn("Запустите панель через sudo.")
    return False


def installed_status(registry: Registry) -> dict[str, bool]:
    """Возвращает {имя: is_installed} для всех install-таргетов."""
    result: dict[str, bool] = {}
    for name, target in registry.get_install_targets().items():
        try:
            result[name] = target.is_installed
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"is_installed failed for {name}")
            err(f"{name}: не удалось проверить статус ({exc})")
            result[name] = False
    return result


def install(registry: Registry, names: list[str]) -> bool:
    if not _require_root("установка компонентов"):
        return False

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
        with console.status(f"[cyan]Устанавливаю {name}…[/]"):
            try:
                installation.install(registry, [name])
                ok(f"{name}: установлен")
            except ServiceError as exc:
                err(f"{name}: {exc}")
                ok_all = False
            except Exception as exc:  # noqa: BLE001
                logger.exception(f"install failed for {name}")
                err(f"{name}: {exc}")
                ok_all = False
    return ok_all


def uninstall(registry: Registry, names: list[str]) -> bool:
    if not _require_root("удаление компонентов"):
        return False

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
        with console.status(f"[cyan]Удаляю {name}…[/]"):
            try:
                installation.uninstall(registry, [name])
                ok(f"{name}: удалён")
            except ServiceError as exc:
                err(f"{name}: {exc}")
                ok_all = False
            except Exception as exc:  # noqa: BLE001
                logger.exception(f"uninstall failed for {name}")
                err(f"{name}: {exc}")
                ok_all = False
    return ok_all


def setup(registry: Registry) -> bool:
    if not _require_root("полная установка (setup)"):
        return False

    from src.infrastructure.manager import configure
    from src.infrastructure.manager import control

    try:
        with console.status("[cyan]Удаляю все компоненты…[/]"):
            installation.uninstall(registry, None)

        with console.status("[cyan]Устанавливаю все компоненты…[/]"):
            installation.install(registry, None)

        with console.status("[cyan]Применяю конфигурацию…[/]"):
            runtime.run(configure.apply_active_users(registry))

        with console.status("[cyan]Перезапускаю сервисы…[/]"):
            control.restart(registry, None)

        ok("setup завершён успешно")
        return True
    except ServiceError as exc:
        err(f"setup: {exc}")
        return False
    except Exception as exc:
        logger.exception("setup failed")
        err(f"setup: {exc}")
        return False
