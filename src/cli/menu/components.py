from src.cli.actions import components as actions
from src.cli.console import console, info
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice
from src.cli.widgets.tables import print_installed


MENU_ITEMS: list[tuple[str, str]] = [
    ("status",     "Что установлено"),
    ("install",    "Установить…"),
    ("uninstall",  "Удалить…"),
    ("setup",      "Полная установка (setup)"),
    ("back",       "Назад"),
]


def run(ctx: CliContext) -> None:
    while True:
        console.clear()
        console.print("[bold cyan]Компоненты[/]")
        console.print()

        choice = prompts.select(
            "Компоненты",
            choices=[Choice(title=label, value=key) for key, label in MENU_ITEMS],
        )

        if choice is None or choice == "back":
            return

        if choice == "status":
            _do_status(ctx)
        elif choice == "install":
            _do_install(ctx)
        elif choice == "uninstall":
            _do_uninstall(ctx)
        elif choice == "setup":
            _do_setup(ctx)


def _all_targets(ctx: CliContext) -> list[str]:
    return list(ctx.registry.get_install_targets().keys())


def _pick_targets(ctx: CliContext, verb: str) -> list[str] | None:
    available = _all_targets(ctx)
    if not available:
        return None

    choices = [Choice(title=name, value=name, checked=False) for name in available]
    selected = prompts.checkbox(
        f"Выберите компоненты для операции «{verb}»",
        choices=choices,
    )
    return selected


def _do_status(ctx: CliContext) -> None:
    console.print()
    with console.status("[cyan]Проверяю установку…[/]"):
        installed = actions.installed_status(ctx.registry)
    console.print()
    print_installed(installed)
    console.print()
    prompts.pause()


def _do_install(ctx: CliContext) -> None:
    targets = _pick_targets(ctx, "установка")
    if targets is None:
        return
    if not targets:
        info("Ничего не выбрано")
        prompts.pause()
        return

    console.print()
    actions.install(ctx.registry, targets)
    console.print()
    prompts.pause()


def _do_uninstall(ctx: CliContext) -> None:
    targets = _pick_targets(ctx, "удаление")
    if targets is None:
        return
    if not targets:
        info("Ничего не выбрано")
        prompts.pause()
        return

    confirm = prompts.confirm(
        f"Удалить {len(targets)} компонент(ов)? Это остановит и снесёт сервисы.",
        default=False,
    )
    if not confirm:
        info("Отменено")
        prompts.pause()
        return

    console.print()
    actions.uninstall(ctx.registry, targets)
    console.print()
    prompts.pause()


def _do_setup(ctx: CliContext) -> None:
    confirm = prompts.confirm(
        "Полная переустановка: удалит ВСЕ компоненты и поставит заново. "
        "Продолжить?",
        default=False,
    )
    if not confirm:
        info("Отменено")
        prompts.pause()
        return

    console.print()
    actions.setup(ctx.registry)
    console.print()
    prompts.pause()
