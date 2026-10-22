from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.infrastructure.system.subprocess import is_root
from src.settings.app import DEBUG, TIMEZONE_HOURS_DELTA


console = Console()


# ---------------------------------------------------------------- output

def ok(msg: str) -> None:
    console.print(f"[green]✓[/] {msg}")


def warn(msg: str) -> None:
    console.print(f"[yellow]![/] {msg}")


def err(msg: str) -> None:
    console.print(f"[red]✗[/] {msg}")


def info(msg: str) -> None:
    console.print(f"[cyan]·[/] {msg}")


def muted(msg: str) -> None:
    console.print(f"[dim]{msg}[/]")


# ---------------------------------------------------------------- header

def _tz_label() -> str:
    if TIMEZONE_HOURS_DELTA == 0:
        return "UTC"
    return f"UTC{TIMEZONE_HOURS_DELTA:+d}"


def print_header(ctx) -> None:
    settings = ctx.settings

    root = "[green]да[/]" if is_root() else "[yellow]нет[/]"
    debug = "[red]on[/]" if DEBUG else "off"

    title = Text("VIKAVPN Manager", style="bold cyan")

    body = Text.from_markup(
        f"Домен: [bold]{settings.tls.domain}[/]    "
        f"TZ: [bold]{_tz_label()}[/]    "
        f"root: {root}    "
        f"debug: {debug}"
    )

    console.print(
        Panel.fit(
            Text.assemble(title, "\n", body),
            border_style="cyan",
            padding=(0, 2),
        )
    )


# ---------------------------------------------------------------- misc

def clear() -> None:
    console.clear()
