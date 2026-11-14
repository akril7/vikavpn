from src.cli.actions import configure as actions
from src.cli.actions.components import filter_installed_names
from src.cli.console import console
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice


MENU_ITEMS: list[tuple[str, str]] = [
    ("apply_pick",    "Применить конфигурацию"),
    ("active_cfg",    "Активная конфигурация"),
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

        if choice == "apply_pick":
            _do_apply_pick(ctx)
        elif choice == "active_cfg":
            _do_active_cfg(ctx)



def _do_apply(ctx: CliContext, names: list[str]):
    console.print()
    actions.apply(ctx.registry, names)
    console.print()
    prompts.pause()


def _do_apply_pick(ctx: CliContext):
    choices = [
        Choice(title=name, value=name, checked=False)
        for name in filter_installed_names(ctx.registry, ctx.registry.names_of_configurators)
    ]
    selected = prompts.checkbox(
        "Выберите configure-таргеты",
        choices=choices,
    )
    if selected is None:
        return

    _do_apply(ctx, selected)


def _do_active_cfg(ctx: CliContext):
    console.print()
    console.print("[bold purple]Доступные установщики[/]")
    console.print(" | ".join(f"[green]{name}[/]" for name in ctx.registry.names_of_installers))
    console.print()
    console.print("[bold purple]Доступные контроллеры[/]")
    console.print(" | ".join(f"[green]{name}[/]" for name in ctx.registry.names_of_controllers))
    console.print()
    console.print("[bold purple]Доступные конфигураторы[/]")
    console.print(" | ".join(f"[green]{name}[/]" for name in ctx.registry.names_of_configurators))
    console.print()
    prompts.pause()
