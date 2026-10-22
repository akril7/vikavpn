from rich.table import Table

from src.cli.console import console
from src.cli.actions.users import UserBrief


def users_table(users: list[UserBrief]) -> Table:
    table = Table(
        title="Пользователи",
        title_style="bold cyan",
        header_style="bold",
        border_style="cyan",
        show_lines=False,
    )
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Имя", style="bold")
    table.add_column("Тариф", justify="center")
    table.add_column("Истекает", justify="center")
    table.add_column("Дней", justify="right")
    table.add_column("TG", justify="center")
    table.add_column("Managed", justify="center")

    for u in users:
        tariff = _tariff_label(u)
        if u.is_active:
            expires = u.sub_expires_at.strftime("%d.%m.%Y %H:%M")
            days = f"[green]{u.days_left}[/]"
        else:
            expires = u.sub_expires_at.strftime("%d.%m.%Y %H:%M")
            days = "[red]0[/]"
        tg = f"[green]● {u.telegram_id}[/]" if u.telegram_id else "[dim]○[/]"
        managed = "[cyan]▸[/]" if u.has_managed else "[dim]·[/]"

        table.add_row(
            str(u.id),
            u.name,
            tariff,
            expires,
            days,
            tg,
            managed,
        )
    return table


def _tariff_label(u: UserBrief) -> str:
    parts = []
    if u.vpn_user:
        parts.append("VPN")
    if u.proxy_user:
        parts.append("Proxy")
    if u.ios_user:
        parts.append("iOS")
    return " + ".join(parts) if parts else "—"

def services_table(statuses: dict[str, bool]) -> Table:
    """Таблица статусов сервисов.

    Args:
        statuses: {имя_сервиса: is_running}
    """
    table = Table(
        title="Статус сервисов",
        title_style="bold cyan",
        show_lines=False,
        header_style="bold",
        border_style="cyan",
    )
    table.add_column("Сервис", style="bold")
    table.add_column("Статус", justify="center")

    for name, is_up in statuses.items():
        if is_up:
            mark = "[green]● active[/]"
        else:
            mark = "[red]○ stopped[/]"
        table.add_row(name, mark)

    return table


def print_services_status(statuses: dict[str, bool]) -> None:
    if not statuses:
        console.print("[yellow]Нет сервисов для отображения[/]")
        return
    console.print(services_table(statuses))


def installed_table(installed: dict[str, bool]) -> Table:
    """Таблица статусов установки компонентов.

    Args:
        installed: {имя_компонента: is_installed}
    """
    table = Table(
        title="Установленные компоненты",
        title_style="bold cyan",
        header_style="bold",
        border_style="cyan",
    )
    table.add_column("Компонент", style="bold")
    table.add_column("Состояние", justify="center")

    for name, is_installed in installed.items():
        if is_installed:
            mark = "[green]✓ установлен[/]"
        else:
            mark = "[red]✗ не установлен[/]"
        table.add_row(name, mark)

    return table


def print_installed(installed: dict[str, bool]) -> None:
    if not installed:
        console.print("[yellow]Нет компонентов для отображения[/]")
        return
    console.print(installed_table(installed))


def kv_table(title: str, rows: dict[str, str]) -> Table:
    """Простая key-value таблица (для настроек, инфо о пользователе)."""
    table = Table(
        title=title,
        title_style="bold cyan",
        show_header=False,
        border_style="cyan",
        padding=(0, 2),
    )
    table.add_column("key", style="bold")
    table.add_column("value")
    for key, value in rows.items():
        table.add_row(key, value)
    return table
