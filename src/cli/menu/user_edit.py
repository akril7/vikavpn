from src.cli.actions import users as actions, configure as cfg_actions
from src.cli.console import console, err, muted, ok
from src.cli.state import CliContext
from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice


MENU_ITEMS: list[tuple[str, str]] = [
    ("set_expire",   "Установить дату окончания"),
    ("toggle_vpn",   "Toggle VPN"),
    ("toggle_proxy", "Toggle Proxy"),
    ("toggle_ios",   "Toggle iOS"),
    ("set_name",     "Изменить имя"),
    ("set_password", "Изменить пароль"),
    ("regen_password", "Перегенерировать пароль"),
    ("set_uuid",     "Перегенерировать UUID"),
    ("bind_msg",     "Привязать мессенджер"),
    ("unbind_msg",   "Отвязать мессенджер"),
    ("add_managed",  "Добавить управляемого"),
    ("del_managed",  "Удалить управляемого"),
    ("delete",       "Удалить пользователя"),
    ("back",         "Назад"),
]


def run(ctx: CliContext, name_or_uuid: str) -> None:
    """Подменю редактирования. name_or_uuid — то, что ввёл пользователь."""
    while True:
        console.clear()
        console.print(f"[bold cyan]Редактирование[/]  [dim]{name_or_uuid}[/]")
        console.print()

        choice = prompts.select(
            "Что сделать?",
            choices=[Choice(title=label, value=key) for key, label in MENU_ITEMS],
        )
        if choice is None or choice == "back":
            return

        _dispatch(ctx, name_or_uuid, choice)


def _dispatch(ctx: CliContext, name_or_uuid: str, action: str) -> None:
    if action == "set_expire":
        _do_set_expire(ctx, name_or_uuid)
    elif action.startswith("toggle_"):
        flag = {
            "toggle_vpn":   "vpn_user",
            "toggle_proxy": "proxy_user",
            "toggle_ios":   "ios_user",
        }[action]
        _mutate(ctx, actions.toggle_flag(name_or_uuid, flag))
    elif action == "set_name":
        _do_set_name(ctx, name_or_uuid)
    elif action == "set_password":
        _do_set_password(ctx, name_or_uuid)
    elif action == "regen_password":
        _mutate(ctx, actions.regen_password(name_or_uuid))
    elif action == "set_uuid":
        _do_set_uuid(ctx, name_or_uuid)
    elif action == "bind_msg":
        _do_bind_messenger(ctx, name_or_uuid)
    elif action == "unbind_msg":
        _do_unbind_messenger(ctx, name_or_uuid)
    elif action == "add_managed":
        _do_add_managed(ctx, name_or_uuid)
    elif action == "del_managed":
        _do_remove_managed(ctx, name_or_uuid)
    elif action == "delete":
        _do_delete(ctx, name_or_uuid)


# ---------------------------------------------------------------- helpers

def _mutate(ctx: CliContext, result: tuple[bool, str]) -> None:
    ok_, msg = result
    if ok_:
        ok(msg)
        cfg_actions.trigger_reload(ctx.settings)
    else:
        err(msg)
    console.print()
    prompts.pause()


# ---------------------------------------------------------------- handlers

def _do_set_expire(ctx: CliContext, name_or_uuid: str) -> None:
    console.print("[dim]Формат: ДД.ММ.ГГГГ ЧЧ:ММ (UTC), например 01.01.2027 00:00[/]")
    text = prompts.text("Дата окончания", default="")
    if not text:
        return
    _mutate(ctx, actions.set_expire(name_or_uuid, text))


def _do_set_name(ctx: CliContext, name_or_uuid: str) -> None:
    new = prompts.text("Новое имя (3–32 символа)")
    if not new:
        return
    _mutate(ctx, actions.set_name(name_or_uuid, new))


def _do_set_password(ctx: CliContext, name_or_uuid: str) -> None:
    new = prompts.password("Новый пароль (мин. 6 символов)")
    if not new:
        return
    _mutate(ctx, actions.set_password(name_or_uuid, new))


def _do_set_uuid(ctx: CliContext, name_or_uuid: str) -> None:
    console.print(
        "[yellow]![/] Смена UUID сломает уже выданные ссылки Clash/TG-proxy."
    )
    confirm = prompts.confirm("Продолжить?", default=False)
    if not confirm:
        return

    import uuid as _uuid
    new_hex = _uuid.uuid4().hex
    _mutate(ctx, actions.set_uuid(name_or_uuid, new_hex))


def _do_bind_messenger(ctx: CliContext, name_or_uuid: str) -> None:
    messenger = prompts.select(
        "Мессенджер",
        choices=[Choice(title="Telegram", value="telegram")],
    )
    if not messenger:
        return
    external_id_text = prompts.text("external_id (число)")
    if not external_id_text:
        return
    try:
        external_id = int(external_id_text)
    except ValueError:
        err("Это не число")
        prompts.pause()
        return
    _mutate(ctx, actions.bind_messenger(name_or_uuid, messenger, external_id))


def _do_unbind_messenger(ctx: CliContext, name_or_uuid: str) -> None:
    messenger = prompts.select(
        "Мессенджер",
        choices=[Choice(title="Telegram", value="telegram")],
    )
    if not messenger:
        return
    _mutate(ctx, actions.unbind_messenger(name_or_uuid, messenger))


def _do_add_managed(ctx: CliContext, name_or_uuid: str) -> None:
    managed_name = prompts.text("Имя управляемого пользователя")
    if not managed_name:
        return
    _mutate(ctx, actions.add_managed(name_or_uuid, managed_name))


def _do_remove_managed(ctx: CliContext, name_or_uuid: str) -> None:
    managed_name = prompts.text("Имя управляемого пользователя")
    if not managed_name:
        return
    _mutate(ctx, actions.remove_managed(name_or_uuid, managed_name))


def _do_delete(ctx: CliContext, name_or_uuid: str) -> None:
    console.print(
        "[red]![/] Это удалит пользователя и все его связи (managed, messenger, payments)."
    )
    confirm = prompts.confirm(
        f"Удалить «{name_or_uuid}»? Это необратимо.",
        default=False,
    )
    if not confirm:
        muted("Отменено")
        prompts.pause()
        return
    _mutate(ctx, actions.delete_user(name_or_uuid))
