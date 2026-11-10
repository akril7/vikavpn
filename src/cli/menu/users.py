from src.application.users.profile import build_profile
from src.cli.actions import configure as cfg_actions
from src.cli.actions import users as actions
from src.cli.console import console, err, info, muted, ok
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice
from src.cli.widgets.tables import kv_table, users_table


MENU_ITEMS: list[tuple[str, str]] = [
    ("list_all",      "Все пользователи"),
    ("card",          "Открыть карточку…"),
    ("create",        "Создать нового"),
    ("back",          "Назад"),
]


def run(ctx: CliContext) -> None:
    while True:
        console.clear()
        console.print("[bold cyan]Пользователи[/]")
        console.print()

        choice = prompts.select(
            "Пользователи",
            choices=[Choice(title=label, value=key) for key, label in MENU_ITEMS],
        )

        if choice is None or choice == "back":
            return

        if choice == "list_all":
            _show_list()
        elif choice == "card":
            _open_card_flow(ctx)
        elif choice == "create":
            _do_create(ctx)


# ---------------------------------------------------------------- list

def _show_list() -> None:
    with console.status("[cyan]Загружаю пользователей…[/]"):
        users = actions.list_users()
    if not users:
        info("Пусто")
        prompts.pause()
        return
    _render_users_pager(users)


def _render_users_pager(users) -> None:
    table = users_table(users)
    with console.pager(styles=True, links=True):
        console.print(table)
        console.print()
        muted(
            "Прокрутка: ↑↓ / PgUp / PgDn, поиск: /, выход: q"
        )


# ---------------------------------------------------------------- card

def _open_card_flow(ctx: CliContext) -> None:
    query = prompts.text(
        "Введите имя или UUID пользователя (полностью)"
    )
    if not query:
        return
    _show_card(ctx, query)


def _show_card(ctx: CliContext, name_or_uuid: str) -> None:
    from src.cli.menu import user_edit

    while True:
        console.clear()
        with console.status("[cyan]Загружаю карточку…[/]"):
            user = actions.get_user(name_or_uuid)

        if user is None:
            err(f"Пользователь «{name_or_uuid}» не найден")
            console.print()
            prompts.pause()
            return

        profile = build_profile(user, ctx.settings)

        console.print()
        rows = {
            "Имя":         user.name,
            "UUID":        user.uuid.hex,
            "Пароль":      user.password,
            "Истекает":    f"{profile.expires_at:%d.%m.%Y %H:%M} (UTC)",
            "Дней":        str(profile.days_left),
            "Активен":     "[green]да[/]" if profile.is_active else "[red]нет[/]",
            "VPN":         "[green]да[/]" if user.vpn_user else "[red]нет[/]",
            "PROXY":       "[green]да[/]" if user.proxy_user else "[red]нет[/]",
            "iOS":         "[green]да[/]" if user.ios_user else "[dim]нет[/]",
            "Telegram":    (f"[green]{profile.telegram_id}[/]"
                            if profile.telegram_id else "[dim]не привязан[/]"),
        }
        console.print(kv_table(f"Пользователь {user.name}", rows))

        console.print()
        console.print("[bold]Ссылки[/]")
        console.print(f"  Clash:      {profile.clash_url or '[dim]—[/]'}")
        console.print(f"  TG-прокси:  {profile.tg_proxy_url or '[dim]—[/]'}")
        console.print(f"  Bot auth:   {profile.bot_auth_url}")
        console.print()

        action = prompts.select(
            "Действие",
            choices=[
                Choice(title="Редактировать", value="edit"),
                Choice(title="Обновить", value="refresh"),
                Choice(title="Назад", value="back"),
            ],
        )
        if action is None or action == "back":
            return
        if action == "refresh":
            continue
        if action == "edit":
            user_edit.run(ctx, name_or_uuid)


# ---------------------------------------------------------------- create

def _do_create(ctx: CliContext) -> None:
    console.print("[bold]Создание пользователя[/]")
    console.print()

    ios = prompts.confirm("iOS-клиент?", default=False)
    if ios is None:
        return

    telegram_id: int | None = None
    bind_tg = prompts.confirm("Привязать Telegram сейчас?", default=False)
    if bind_tg is None:
        return
    if bind_tg:
        tg_text = prompts.text("Telegram ID (число)")
        if tg_text is None:
            return
        try:
            telegram_id = int(tg_text.strip())
        except ValueError:
            err("Telegram ID — это число")
            prompts.pause()
            return

    console.print()
    with console.status("[cyan]Создаю пользователя…[/]"):
        ok_, msg = actions.create_user(
            ios_user=bool(ios),
            telegram_id=telegram_id
        )

    if ok_:
        ok(msg)
        cfg_actions.trigger_reload(ctx.settings)
    else:
        err(msg)

    console.print()
    prompts.pause()
