from src.cli.actions import configure as actions
from src.cli.console import console
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice


MENU_ITEMS: list[tuple[str, str]] = [
    ("apply_all",     "Применить конфигурацию (все)"),
    ("apply_pick",    "Применить конфигурацию (выбрать)…"),
    ("back",          "Назад"),
]


def run(ctx: CliContext) -> None:
    while True:
        console.clear()
        console.print("[bold cyan]Конфигурация[/]")
        console.print()

        choice = prompts.select(
            "Конфигурация",
            choices=[Choice(title=label, value=key) for key, label in MENU_ITEMS],
        )

        if choice is None or choice == "back":
            return

        if choice == "apply_all":
            _do_apply(ctx, ctx.registry.get_names_of_configurator())
        elif choice == "apply_pick":
            _do_apply_pick(ctx)


def _do_apply(ctx: CliContext, names: list[str]) -> None:
    console.print()
    actions.apply(ctx.registry, names)
    console.print()
    prompts.pause()


def _do_apply_pick(ctx: CliContext) -> None:
    choices = [
        Choice(title=name, value=name, checked=False)
        for name in ctx.registry.get_names_of_configurator()
    ]
    selected = prompts.checkbox(
        "Выберите configure-таргеты",
        choices=choices,
    )
    if selected is None:
        return

    _do_apply(ctx, selected)
