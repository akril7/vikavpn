from loguru import logger

from src.application.ports.services import ServiceError
from src.application.ports.registry import RegistryLike
from src.application.services.orchestration import installation
from src.application.services.orchestration import control
from src.bootstrap.composition.loaders import apply_active_users
from src.cli.async_runtime import runtime
from src.cli.console import console, err, ok, warn
from src.cli.utils.root import require_root


def install(registry: RegistryLike, names: list[str]) -> bool:
    if not require_root("установка компонентов"):
        return False

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
        with console.status(f"[cyan]Устанавливаю {name}...[/]"):
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


def uninstall(registry: RegistryLike, names: list[str]) -> bool:
    if not require_root("удаление компонентов"):
        return False

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
        with console.status(f"[cyan]Удаляю {name}...[/]"):
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


def setup(registry: RegistryLike, names: list[str]) -> bool:
    if not require_root("полная установка (setup)"):
        return False

    try:
        with console.status("[cyan]Удаляю все компоненты…[/]"):
            installation.uninstall(registry,
                                   names=list(filter(lambda x: x in registry.names_of_installers, names)))

        with console.status("[cyan]Устанавливаю все компоненты…[/]"):
            installation.install(registry,
                                 names=list(filter(lambda x: x in registry.names_of_installers, names)))

        with console.status("[cyan]Применяю конфигурацию…[/]"):
            runtime.run(apply_active_users(registry,
                                           names=list(filter(lambda x: x in registry.names_of_configurators, names))))

        with console.status("[cyan]Перезапускаю сервисы…[/]"):
            control.restart(registry,
                            names=list(filter(lambda x: x in registry.names_of_controllers, names)))

        ok("setup завершён успешно")
        return True
    except ServiceError as exc:
        err(f"setup: {exc}")
        return False
    except Exception as exc:
        logger.exception("setup failed")
        err(f"setup: {exc}")
        return False
