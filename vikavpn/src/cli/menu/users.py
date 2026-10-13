from src.cli.actions import configure as cfg_actions
from src.cli.actions import users as actions
from src.cli.console import console, err, info, muted, ok
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice
from src.cli.widgets.tables import kv_table, users_table


MENU_ITEMS: list[tuple[str, str]] = [
    ("list_all",      "Все пользователи"),
    ("list_active",   "Активные"),
    ("list_expired",  "Истёкшие"),
    ("list_vpn",      "С VPN"),
    ("list_proxy",    "С Proxy"),
    ("list_ios",      "С iOS"),
    ("search",        "Поиск по имени / UUID"),
    ("card",          "Открыть карточку…"),
    ("create",        "Создать нового"),
    ("import",        "Импорт из TOML"),
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

        if choice.startswith("list_"):
            _show_list(ctx, choice.removeprefix("list_"))
        elif choice == "search":
            _do_search(ctx)
        elif choice == "card":
            _open_card_flow(ctx)
        elif choice == "create":
            _do_create(ctx)
        elif choice == "import":
            _do_import(ctx)


# ---------------------------------------------------------------- list

def _show_list(ctx: CliContext, kind: str) -> None:
    with console.status("[cyan]Загружаю пользователей…[/]"):
        users = actions.list_users(filter_kind=kind)
    if not users:
        info("Пусто")
        prompts.pause()
        return
    _render_users_pager(users, title=_list_title(kind))


def _list_title(kind: str) -> str:
    return {
        "all":     "Все пользователи",
        "active":  "Активные",
        "expired": "Истёкшие",
        "vpn":     "С VPN",
        "proxy":   "С Proxy",
        "ios":     "С iOS",
    }.get(kind, "Пользователи")


def _render_users_pager(users, title: str) -> None:
    table = users_table(users)
    with console.pager(styles=True, links=True):
        console.print(table)
        console.print()
        muted(
            "Прокрутка: ↑↓ / PgUp / PgDn, поиск: /, выход: q"
        )


# ---------------------------------------------------------------- search

def _do_search(ctx: CliContext) -> None:
    query = prompts.text("Введите имя или UUID (частично)")
    if not query:
        return
    with console.status("[cyan]Ищу…[/]"):
        users = actions.list_users(filter_kind="all", search=query)
    if not users:
        info("Ничего не найдено")
        prompts.pause()
        return
    _render_users_pager(users, title=f"Поиск: {query}")


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
            full = actions.get_user_full(name_or_uuid, ctx.settings)

        if full is None:
            err(f"Пользователь «{name_or_uuid}» не найден")
            console.print()
            prompts.pause()
            return

        b = full.brief

        console.print()
        rows = {
            "ID":          str(b.id),
            "Имя":         b.name,
            "UUID":        b.uuid_hex,
            "Пароль":      full.password,
            "Истекает":    f"{b.sub_expires_at:%d.%m.%Y %H:%M} (UTC)",
            "Дней":        str(b.days_left),
            "Активен":     "[green]да[/]" if b.is_active else "[red]нет[/]",
            "VPN":         "[green]да[/]" if b.vpn_user else "[dim]нет[/]",
            "Proxy":       "[green]да[/]" if b.proxy_user else "[dim]нет[/]",
            "iOS":         "[green]да[/]" if b.ios_user else "[dim]нет[/]",
            "Telegram":    (f"[green]{b.telegram_id}[/]"
                            if b.telegram_id else "[dim]не привязан[/]"),
            "Управляет":   ", ".join(full.managed_names) if full.managed_names else "—",
            "Управляется": ", ".join(full.manager_names) if full.manager_names else "—",
        }
        console.print(kv_table(f"Пользователь {b.name}", rows))

        console.print()
        console.print("[bold]Ссылки[/]")
        console.print(f"  Clash:      {full.clash_url or '[dim]—[/]'}")
        console.print(f"  TG-прокси:  {full.tg_proxy_url or '[dim]—[/]'}")
        console.print(f"  Bot auth:   {full.bot_auth_url}")
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
    console.print("[dim]Enter — оставить сгенерированное значение.[/]")
    console.print()

    # 1. Имя
    default_name = actions.suggest_name()
    name = prompts.text("Имя", default=default_name)
    if name is None:
        return
    name = name.strip() or default_name

    # 2. Пароль
    default_password = actions.suggest_password()
    password = prompts.text("Пароль", default=default_password)
    if password is None:
        return
    password = password.strip() or default_password

    # 3. UUID
    default_uuid = actions.suggest_uuid()
    uuid_hex = prompts.text("UUID (hex)", default=default_uuid)
    if uuid_hex is None:
        return
    uuid_hex = uuid_hex.strip() or default_uuid

    # 4. Trial
    trial_text = prompts.text("Trial-период, дней", default="7")
    if trial_text is None:
        return
    try:
        trial_days = int(trial_text.strip() or "7")
    except ValueError:
        err("Trial — это число")
        prompts.pause()
        return

    # 5. Флаги
    vpn = prompts.confirm("VPN-доступ?", default=True)
    if vpn is None:
        return
    proxy = prompts.confirm("Proxy-доступ (MTProxyL)?", default=True)
    if proxy is None:
        return
    ios = prompts.confirm("iOS-клиент?", default=False)
    if ios is None:
        return

    # 6. Telegram
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

    spec = actions.CreateUserSpec(
        name=name,
        password=password,
        uuid_hex=uuid_hex,
        trial_days=trial_days,
        vpn_user=bool(vpn),
        proxy_user=bool(proxy),
        ios_user=bool(ios),
        telegram_id=telegram_id,
    )

    console.print()
    with console.status("[cyan]Создаю пользователя…[/]"):
        ok_, msg = actions.create_user(spec)

    if ok_:
        ok(msg)
        cfg_actions.trigger_reload(ctx.settings)
    else:
        err(msg)

    console.print()
    prompts.pause()


# ---------------------------------------------------------------- import

def _do_import(ctx: CliContext) -> None:
    console.print(
        "[dim]Путь к TOML-файлу. Например: users.toml или /root/users.toml[/]"
    )
    path = prompts.text("Путь к файлу")
    if not path:
        return

    console.print()
    with console.status("[cyan]Импортирую…[/]"):
        ok_, msg = actions.import_users(path)

    if ok_:
        ok(msg)
        cfg_actions.trigger_reload(ctx.settings)

        console.print()
        apply_now = prompts.confirm(
            "Применить конфигурацию сейчас?", default=True,
        )
        if apply_now:
            with console.status("[cyan]Применяю конфигурацию…[/]"):
                from src.cli.actions import configure as cfg_actions
                cfg_actions.apply(ctx.registry)
    else:
        err(msg)

    console.print()
    prompts.pause()
