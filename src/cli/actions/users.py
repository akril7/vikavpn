import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from loguru import logger
from sqlalchemy import select

from src.cli.async_runtime import runtime
from src.core.url_build.file import build_origin, build_clash_config_url
from src.core.url_build.link import (
    build_bot_auth_url,
    build_telegram_proxy_url,
)
from src.core.users.importer import import_users_from_file
from src.core.utils.dt import utcnow
from src.db.connection import Session
from src.db.models import User
from src.db.repo import UserRepository, options
from src.settings import Settings

from src.core.users.flow.registration import generate_password, WORDS_DICT
from src.db.enums import Messenger
from src.db.repo.messager import MessengerAlreadyBoundError


@dataclass
class UserBrief:
    id: int
    name: str
    uuid_hex: str
    is_active: bool
    vpn_user: bool
    proxy_user: bool
    ios_user: bool
    sub_expires_at: datetime
    days_left: int
    telegram_id: int | None
    has_managed: bool


@dataclass
class UserFull:
    brief: UserBrief
    password: str
    managed_names: list[str]
    manager_names: list[str]
    clash_url: str | None
    tg_proxy_url: str | None
    bot_auth_url: str


# ---------------------------------------------------------------- list

def list_users(
        *,
        filter_kind: str = "all",
        search: str | None = None,
) -> list[UserBrief]:
    """Возвращает список пользователей с фильтром/поиском.

    filter_kind: all | active | expired | vpn | proxy | ios
    search: подстрока для поиска по имени/uuid
    """
    return runtime.run(_list_users(filter_kind, search))


async def _list_users(filter_kind: str, search: str | None) -> list[UserBrief]:
    async with Session() as session:
        repo = UserRepository(session)
        stmt = select(User).order_by(User.id)

        if filter_kind == "active":
            from src.core.utils.dt import utcnow
            stmt = stmt.where(User.sub_expires_at > utcnow())
        elif filter_kind == "expired":
            from src.core.utils.dt import utcnow
            stmt = stmt.where(User.sub_expires_at <= utcnow())
        elif filter_kind == "vpn":
            stmt = stmt.where(User.vpn_user.is_(True))
        elif filter_kind == "proxy":
            stmt = stmt.where(User.proxy_user.is_(True))
        elif filter_kind == "ios":
            stmt = stmt.where(User.ios_user.is_(True))

        stmt = stmt.options(*options.messenger_options(), *options.managed_options())

        users = list((await session.scalars(stmt)).all())

        if search:
            needle = search.lower()
            users = [
                u for u in users
                if needle in u.name.lower()
                   or needle in u.uuid.hex.lower()
            ]

        return [_to_brief(u) for u in users]


def _to_brief(user: User) -> UserBrief:
    from src.core.utils.dt import utcnow

    now = utcnow()
    days_left = max(0, (user.sub_expires_at.date() - now.date()).days)
    return UserBrief(
        id=user.id,
        name=user.name,
        uuid_hex=user.uuid.hex,
        is_active=user.is_active,
        vpn_user=user.vpn_user,
        proxy_user=user.proxy_user,
        ios_user=user.ios_user,
        sub_expires_at=user.sub_expires_at,
        days_left=days_left,
        telegram_id=user.telegram_id,
        has_managed=bool(user.managed_links),
    )


# ---------------------------------------------------------------- full info

def get_user_full(name_or_uuid: str, settings: Settings) -> UserFull | None:
    return runtime.run(_get_user_full(name_or_uuid, settings))


async def _get_user_full(name_or_uuid: str, settings: Settings) -> UserFull | None:
    async with Session() as session:
        repo = UserRepository(session)

        user = await repo.get_by_name(
            name_or_uuid,
            options=options.messenger_options()
                    + options.managed_options()
                    + options.manager_options(),
        )
        if user is None:
            try:
                uuid = UUID(hex=name_or_uuid)
            except (ValueError, TypeError):
                return None
            user = await repo.get_by_uuid(
                uuid,
                options=options.messenger_options()
                        + options.managed_options()
                        + options.manager_options(),
            )
        if user is None:
            return None

        brief = _to_brief(user)

        origin = build_origin(settings.tls.domain, settings.site.port)

        clash_url = (
            build_clash_config_url(user, origin, settings.clash.configs_urlpath)
            if user.vpn_user else None
        )
        tg_proxy_url = (
            build_telegram_proxy_url(
                user,
                settings.mtproxyl.sni,
                settings.tls.domain,
                settings.mtproxyl.port,
            )
            if user.proxy_user else None
        )
        bot_auth_url = build_bot_auth_url(settings.telegram_bot.username, user)

        managed_names = [
            link.managed.name
            for link in user.managed_links
            if link.managed is not None
        ]
        manager_names = [
            link.manager.name
            for link in user.manager_links
            if link.manager is not None
        ]

        return UserFull(
            brief=brief,
            password=user.password,
            managed_names=managed_names,
            manager_names=manager_names,
            clash_url=clash_url,
            tg_proxy_url=tg_proxy_url,
            bot_auth_url=bot_auth_url,
        )


# ---------------------------------------------------------------- mutations

def set_expire(name_or_uuid: str, until_text: str) -> tuple[bool, str]:
    """Установить дату окончания. until_text — 'dd.mm.YYYY HH:MM' или 'dd.mm.YYYY'."""
    return runtime.run(_set_expire(name_or_uuid, until_text))


async def _set_expire(name_or_uuid: str, until_text: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository

    until = _parse_until(until_text)
    if until is None:
        return False, "Неверный формат даты. Ожидается «ДД.ММ.ГГГГ ЧЧ:ММ» или «ДД.ММ.ГГГГ»."

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        user.sub_expires_at = until
        await session.commit()
        return True, f"{user.name}: дата окончания → {until:%d.%m.%Y %H:%M} UTC"


def _parse_until(text: str):
    from datetime import UTC, datetime
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


async def _find_user(repo, name_or_uuid: str):
    user = await repo.get_by_name(name_or_uuid)
    if user is not None:
        return user
    try:
        uuid = UUID(hex=name_or_uuid)
    except (ValueError, TypeError):
        return None
    return await repo.get_by_uuid(uuid)


# ---------------------------------------------------------------- toggles

def toggle_flag(name_or_uuid: str, flag: str) -> tuple[bool, str]:
    """flag: 'vpn_user' | 'proxy_user' | 'ios_user'"""
    return runtime.run(_toggle_flag(name_or_uuid, flag))


async def _toggle_flag(name_or_uuid: str, flag: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        new_value = not bool(getattr(user, flag))
        setattr(user, flag, new_value)
        await session.commit()
        return True, f"{user.name}: {flag} → {'да' if new_value else 'нет'}"


# ---------------------------------------------------------------- name/password/uuid

def set_name(name_or_uuid: str, new_name: str) -> tuple[bool, str]:
    return runtime.run(_set_name(name_or_uuid, new_name))


async def _set_name(name_or_uuid: str, new_name: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository

    new_name = new_name.strip()
    if not (3 <= len(new_name) <= 32):
        return False, "Имя должно быть от 3 до 32 символов"

    async with Session() as session:
        repo = UserRepository(session)
        if await repo.exists_by_name(new_name):
            return False, f"Имя «{new_name}» уже занято"

        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        old = user.name
        user.name = new_name
        await session.commit()
        return True, f"{old} → {new_name}"


def set_password(name_or_uuid: str, new_password: str) -> tuple[bool, str]:
    return runtime.run(_set_password(name_or_uuid, new_password))


async def _set_password(name_or_uuid: str, new_password: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository

    if len(new_password) < 6:
        return False, "Пароль должен быть не короче 6 символов"

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        user.password = new_password
        await session.commit()
        return True, f"{user.name}: пароль изменён"


def regen_password(name_or_uuid: str) -> tuple[bool, str]:
    new_password = generate_password()
    ok, msg = set_password(name_or_uuid, new_password)
    if ok:
        return True, f"Новый пароль: {new_password}"
    return ok, msg


def set_uuid(name_or_uuid: str, new_uuid_hex: str) -> tuple[bool, str]:
    return runtime.run(_set_uuid(name_or_uuid, new_uuid_hex))


async def _set_uuid(name_or_uuid: str, new_uuid_hex: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository
    from uuid import UUID

    try:
        new_uuid = UUID(hex=new_uuid_hex)
    except (ValueError, TypeError):
        return False, "Некорректный UUID"

    async with Session() as session:
        repo = UserRepository(session)
        if await repo.exists_by_uuid(new_uuid):
            return False, "UUID уже используется"

        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        old = user.uuid.hex
        user.uuid = new_uuid
        await session.commit()
        return True, f"UUID: {old} → {new_uuid.hex}"


# ---------------------------------------------------------------- messenger

def unbind_messenger(name_or_uuid: str, messenger_value: str) -> tuple[bool, str]:
    return runtime.run(_unbind_messenger(name_or_uuid, messenger_value))


async def _unbind_messenger(name_or_uuid: str, messenger_value: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository, UserMessengerRepository

    try:
        messenger = Messenger(messenger_value)
    except ValueError:
        return False, f"Неизвестный мессенджер: {messenger_value}"

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        bound = await UserMessengerRepository(session).unbind(
            user_id=user.id, messenger=messenger,
        )
        await session.commit()
        if bound:
            return True, f"{user.name}: {messenger.value} отвязан"
        return False, f"{user.name}: {messenger.value} и так не привязан"


def bind_messenger(
        name_or_uuid: str, messenger_value: str, external_id: int,
) -> tuple[bool, str]:
    return runtime.run(_bind_messenger(name_or_uuid, messenger_value, external_id))


async def _bind_messenger(
        name_or_uuid: str, messenger_value: str, external_id: int,
) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository, UserMessengerRepository

    try:
        messenger = Messenger(messenger_value)
    except ValueError:
        return False, f"Неизвестный мессенджер: {messenger_value}"

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        try:
            await UserMessengerRepository(session).bind(
                user_id=user.id,
                messenger=messenger,
                external_id=external_id,
            )
        except MessengerAlreadyBoundError as exc:
            return False, str(exc)

        await session.commit()
        return True, f"{user.name}: {messenger.value} → {external_id}"


# ---------------------------------------------------------------- managed

def add_managed(manager_name: str, managed_name: str) -> tuple[bool, str]:
    return runtime.run(_add_managed(manager_name, managed_name))


async def _add_managed(manager_name: str, managed_name: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository, UserManagementRepository

    if manager_name == managed_name:
        return False, "Пользователь не может управлять сам собой"

    async with Session() as session:
        repo = UserRepository(session)
        manager = await repo.get_by_name(manager_name)
        managed = await repo.get_by_name(managed_name)
        if manager is None:
            return False, f"Менеджер «{manager_name}» не найден"
        if managed is None:
            return False, f"Пользователь «{managed_name}» не найден"

        mgmt = UserManagementRepository(session)
        exists = await mgmt.exists(
            manager_id=manager.id, managed_id=managed.id,
        )
        if exists:
            return False, "Связь уже существует"

        await mgmt.create(manager_id=manager.id, managed_id=managed.id)
        await session.commit()
        return True, f"{manager_name} теперь управляет {managed_name}"


def remove_managed(manager_name: str, managed_name: str) -> tuple[bool, str]:
    return runtime.run(_remove_managed(manager_name, managed_name))


async def _remove_managed(manager_name: str, managed_name: str) -> tuple[bool, str]:
    from sqlalchemy import delete as sql_delete

    from src.db.connection import Session
    from src.db.models import UserManagement
    from src.db.repo import UserRepository

    async with Session() as session:
        repo = UserRepository(session)
        manager = await repo.get_by_name(manager_name)
        managed = await repo.get_by_name(managed_name)
        if manager is None or managed is None:
            return False, "Один из пользователей не найден"

        stmt = sql_delete(UserManagement).where(
            UserManagement.manager_id == manager.id,
            UserManagement.managed_id == managed.id,
        )
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount > 0:
            return True, f"Связь {manager_name} → {managed_name} удалена"
        return False, "Связи не было"


# ---------------------------------------------------------------- delete

def delete_user(name_or_uuid: str) -> tuple[bool, str]:
    return runtime.run(_delete_user(name_or_uuid))


async def _delete_user(name_or_uuid: str) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.repo import UserRepository

    async with Session() as session:
        repo = UserRepository(session)
        user = await _find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        name = user.name
        await repo.delete(user)
        await session.commit()
        return True, f"Пользователь {name} удалён"


# ---------------------------------------------------------------- create

@dataclass
class CreateUserSpec:
    name: str
    password: str
    uuid_hex: str
    trial_days: int
    vpn_user: bool
    proxy_user: bool
    ios_user: bool
    telegram_id: int | None


def suggest_name() -> str:
    return f"{secrets.choice(WORDS_DICT)}_{uuid4().hex[:8]}"


def suggest_password() -> str:
    return generate_password()


def suggest_uuid() -> str:
    return uuid4().hex


def create_user(spec: CreateUserSpec) -> tuple[bool, str]:
    return runtime.run(_create_user(spec))


async def _create_user(spec: CreateUserSpec) -> tuple[bool, str]:
    from src.db.connection import Session
    from src.db.enums import Messenger
    from src.db.repo import (
        UserRepository,
        UserMessengerRepository,
    )

    if not (3 <= len(spec.name) <= 32):
        return False, "Имя должно быть от 3 до 32 символов"
    if len(spec.password) < 6:
        return False, "Пароль должен быть не короче 6 символов"
    try:
        user_uuid = UUID(hex=spec.uuid_hex)
    except (ValueError, TypeError):
        return False, "Некорректный UUID"
    if spec.trial_days < 0:
        return False, "Trial-период не может быть отрицательным"

    async with Session() as session:
        repo = UserRepository(session)
        if await repo.exists_by_name(spec.name):
            return False, f"Имя «{spec.name}» уже занято"
        if await repo.exists_by_uuid(user_uuid):
            return False, "UUID уже используется"

        user = await repo.create(
            name=spec.name,
            password=spec.password,
            uuid=user_uuid,
            sub_expires_at=utcnow() + timedelta(days=spec.trial_days),
            vpn_user=spec.vpn_user,
            proxy_user=spec.proxy_user,
            ios_user=spec.ios_user,
        )

        if spec.telegram_id is not None:
            try:
                await UserMessengerRepository(session).bind(
                    user_id=user.id,
                    messenger=Messenger.TELEGRAM,
                    external_id=spec.telegram_id,
                )
            except MessengerAlreadyBoundError as exc:
                await session.rollback()
                return False, f"Telegram ID уже привязан: {exc}"

        await session.commit()

    return True, f"Пользователь {spec.name} создан (trial {spec.trial_days} дн.)"


# ---------------------------------------------------------------- import

def import_users(path: str) -> tuple[bool, str]:
    return runtime.run(_import_users(path))


async def _import_users(path: str) -> tuple[bool, str]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return False, f"Файл не найден: {p}"
    if not p.is_file():
        return False, f"Это не файл: {p}"

    try:
        count = await import_users_from_file(str(p))
    except Exception as exc:  # noqa: BLE001
        logger.exception("import_users_from_file failed")
        return False, f"Ошибка импорта: {exc}"

    return True, f"Импортировано пользователей: {count}"
