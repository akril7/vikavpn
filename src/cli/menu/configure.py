from src.cli.actions import configure as actions
from src.cli.console import console, info, muted
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice
from src.cli.widgets.tables import kv_table


MENU_ITEMS: list[tuple[str, str]] = [
    ("apply_all",     "Применить конфигурацию (все)"),
    ("apply_pick",    "Применить конфигурацию (выбрать)…"),
    ("view",          "Показать текущие настройки"),
    ("edit_env",      "Открыть .env в редакторе"),
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
            _do_apply(ctx, names=None)
        elif choice == "apply_pick":
            _do_apply_pick(ctx)
        elif choice == "view":
            _do_view(ctx)
        elif choice == "edit_env":
            _do_edit_env(ctx)


def _do_apply(ctx: CliContext, names: list[str] | None) -> None:
    console.print()
    actions.apply(ctx.registry, names)
    console.print()
    prompts.pause()


def _do_apply_pick(ctx: CliContext) -> None:
    available = list(ctx.registry.get_configure_targets().keys())
    if not available:
        info("Нет доступных configure-таргетов")
        prompts.pause()
        return

    choices = [Choice(title=name, value=name, checked=False) for name in available]
    selected = prompts.checkbox(
        "Выберите configure-таргеты",
        choices=choices,
    )
    if selected is None:
        return
    if not selected:
        info("Ничего не выбрано")
        prompts.pause()
        return

    _do_apply(ctx, names=selected)


def _do_view(ctx: CliContext) -> None:
    console.print()
    rows = _settings_rows(ctx)
    console.print(kv_table("Текущие настройки", rows))
    console.print()
    prompts.pause()


def _settings_rows(ctx: CliContext) -> dict[str, str]:
    s = ctx.settings
    return {
        "Домен":            s.tls.domain,
        "TLS cert":         str(s.tls.cert_path),
        "TLS key":          str(s.tls.key_path),
        "Порт сайта":       str(s.site.port),
        "Доп. порты":       ", ".join(str(p) for p in s.site.extra_ports),
        "Clash URL path":   s.clash.configs_urlpath,
        "Clash store dir":  str(s.clash.configs_store_dir),
        "Mita port range":  s.mita.port_range,
        "Mita protocol":    str(s.mita.protocol),
        "Hysteria port":    str(s.hysteria.port),
        "Hysteria auth":    s.hysteria.auth_url,
        "TrustTunnel port": str(s.trusttunnel.port),
        "TrustTunnel SNI":  s.trusttunnel.sni,
        "MTProxyL port":    str(s.mtproxyl.port),
        "MTProxyL SNI":     s.mtproxyl.sni,
        "MTProxyL mode":    str(s.mtproxyl.mode),
        "Yoomoney receiver": s.yoomoney.receiver,
        "Yoomoney fee":     f"{s.yoomoney.fee_percent}%",
        "Reloader URL":     s.reloader.url,
        "Payments URL":     s.payments.origin,
        "Telegram bot":     s.telegram_bot.username,
    }


def _do_edit_env(ctx: CliContext) -> None:
    opened, _ = actions.open_env_and_maybe_restart()
    if not opened:
        console.print()
        prompts.pause()
        return

    console.print()
    info("Файл .env сохранён. Перечитываю настройки…")
    ctx.reload()
    console.print("[green]✓[/] Настройки перечитаны")

    console.print()
    restart = prompts.confirm(
        "Перезапустить все сервисы, чтобы применить изменения?",
        default=False,
    )
    if not restart:
        muted("Сервисы не тронуты. Изменения применятся при следующем запуске.")
        console.print()
        prompts.pause()
        return

    console.print()
    actions.restart_all(ctx.registry)
    console.print()
    prompts.pause()
