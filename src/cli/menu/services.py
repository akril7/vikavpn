from src.cli.actions import services as actions
from src.cli.console import console, info
from src.cli.state import CliContext
from src.cli.utils import systemd
from src.cli.widgets import prompts
from src.cli.widgets.logs import show_logs
from src.cli.widgets.prompts import Choice
from src.cli.widgets.tables import print_services_status


MENU_ITEMS: list[tuple[str, str]] = [
    ("status",   "Статус"),
    ("start",    "Запустить…"),
    ("stop",     "Остановить…"),
    ("restart",  "Перезапустить…"),
    ("reload",   "Перезагрузить конфиг…"),
    ("logs",     "Логи (live)…"),
    ("back",     "Назад"),
]


def _pick_targets(ctx: CliContext, verb: str) -> list[str] | None:
    available = list(ctx.registry.get_control_targets().keys())
    if not available:
        return None

    choices = [Choice(title=name, value=name, checked=False) for name in available]
    selected = prompts.checkbox(
        f"Выберите сервисы для операции «{verb}»",
        choices=choices,
    )
    if selected is None:
        return None
    return selected


def run(ctx: CliContext) -> None:
    while True:
        console.clear()
        _print_title()
        choice = prompts.select(
            "Сервисы",
            choices=[Choice(title=label, value=key) for key, label in MENU_ITEMS],
        )

        if choice is None or choice == "back":
            return

        if choice == "status":
            _do_status(ctx)
        elif choice == "logs":
            _do_logs()
        else:
            _do_action(ctx, choice)


def _print_title() -> None:
    console.print("[bold cyan]Сервисы[/]")
    console.print()


def _do_status(ctx: CliContext) -> None:
    console.print()
    with console.status("[cyan]Опрашиваю статусы…[/]"):
        statuses = actions.status(ctx.registry)
    console.print()
    print_services_status(statuses)
    console.print()
    prompts.pause()


def _do_logs() -> None:
    units = systemd.list_units()
    if not units:
        info("Не найдено ни одного подходящего systemd-юнита")
        prompts.pause()
        return

    choice = prompts.select(
        "Выберите сервис для просмотра логов",
        choices=[
            Choice(title=unit, value=unit)
            for unit in units
        ],
    )
    if choice is None:
        return

    console.print(f"[dim]Открываю логи {choice}. Выход — Ctrl+C.[/]")
    import time
    time.sleep(0.4)

    show_logs(choice)

    console.print()
    info(f"Просмотр логов {choice} завершён")
    prompts.pause()


def _do_action(ctx: CliContext, action: str) -> None:
    verb = {
        "start":   "запуск",
        "stop":    "остановка",
        "restart": "перезапуск",
        "reload":  "перезагрузка конфига",
    }[action]

    targets = _pick_targets(ctx, verb)
    if targets is None:
        return
    if not targets:
        info("Ничего не выбрано")
        prompts.pause()
        return

    console.print()
    if action == "start":
        actions.start(ctx.registry, targets)
    elif action == "stop":
        actions.stop(ctx.registry, targets)
    elif action == "restart":
        actions.restart(ctx.registry, targets)
    elif action == "reload":
        actions.reload(ctx.registry, targets)

    console.print()
    prompts.pause()
