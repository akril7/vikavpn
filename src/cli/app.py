from src.cli.async_runtime import runtime
from src.db.connection import create_tables
from src.infrastructure.manager.registry import Registry
from src.infrastructure.system.subprocess import is_root
from src.settings import Settings

from src.cli import console as ui
from src.cli.menu import main as menu_main
from src.cli.state import CliContext


def run() -> None:
    settings = Settings()
    registry = Registry(settings)
    ctx = CliContext(settings=settings, registry=registry)

    runtime.run(create_tables())

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
        from loguru import logger
        logger.exception("Panel action failed")
        from src.cli.widgets import prompts
        prompts.pause()
