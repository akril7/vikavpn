from loguru import logger

from src.cli.async_runtime import runtime
from src.infrastructure.network.socks import install_socks_proxy
from src.infrastructure.persistence.connection import create_tables
from src.bootstrap.registry import Registry
from src.infrastructure.system.subprocess import is_root
from src.configuration import Settings

from src.cli import console as ui
from src.cli.menu import main as menu_main
from src.cli.state import CliContext


def run() -> None:
    settings = Settings()
    registry = Registry(settings)
    ctx = CliContext(settings=settings, registry=registry)

    if settings.proxy.enabled:
        install_socks_proxy(settings.proxy.host, settings.proxy.port)

    logger.debug("Connect to db...")
    runtime.run(create_tables())
    logger.debug("Connected")

    if not is_root():
        ui.warn(
            "Вы не root. Часть операций (установка, управление сервисами) "
            "будет недоступна."
        )
        ui.console.print()

    try:
        while True:
            ui.clear()
            ui.print_header(ctx)
            ui.console.print()

            choice = menu_main.main_menu()

            if choice is None or choice == "exit":
                break

            ui.console.print()
            _dispatch(choice, ctx)
    except KeyboardInterrupt:
        pass
    finally:
        runtime.shutdown()

    ui.console.print()
    ui.muted("Выход.")


def _dispatch(key: str, ctx: CliContext) -> None:
    if key == "components":
        from src.cli.menu import components as mod
    elif key == "configure":
        from src.cli.menu import configure as mod
    elif key == "services":
        from src.cli.menu import services as mod
    elif key == "users":
        from src.cli.menu import users as mod
    else:
        ui.info(f"Неизвестный раздел: {key}")
        return

    try:
        mod.run(ctx)
    except KeyboardInterrupt:
        ui.console.print()
    except Exception as exc:  # noqa: BLE001
        ui.err(f"Ошибка: {exc}")
        logger.exception("Panel action failed")
        from src.cli.widgets import prompts
        prompts.pause()
