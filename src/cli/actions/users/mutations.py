from uuid import UUID

from src.cli.async_runtime import runtime
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository

from .utils import find_user, parse_until


def set_name(name_or_uuid: str, new_name: str) -> tuple[bool, str]:
    return runtime.run(_set_name(name_or_uuid, new_name))


async def _set_name(name_or_uuid: str, new_name: str) -> tuple[bool, str]:
    new_name = new_name.strip()

    async with Session() as session:
        repo = UserRepository(session)
        if await repo.exists_by_name(new_name):
            return False, f"Имя «{new_name}» уже занято"

        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        old = user.name
        user.name = new_name
        await session.commit()
        return True, f"{old} → {new_name}"


def set_password(name_or_uuid: str, new_password: str) -> tuple[bool, str]:
    return runtime.run(_set_password(name_or_uuid, new_password))


async def _set_password(name_or_uuid: str, new_password: str) -> tuple[bool, str]:
    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        user.password = new_password
        await session.commit()
        return True, f"{user.name}: пароль изменён"


def set_uuid(name_or_uuid: str, new_uuid_hex: str) -> tuple[bool, str]:
    return runtime.run(_set_uuid(name_or_uuid, new_uuid_hex))


async def _set_uuid(name_or_uuid: str, new_uuid_hex: str) -> tuple[bool, str]:
    try:
        new_uuid = UUID(hex=new_uuid_hex)
    except (ValueError, TypeError):
        return False, "Некорректный UUID"

    async with Session() as session:
        repo = UserRepository(session)
        if await repo.exists_by_uuid(new_uuid):
            return False, "UUID уже используется"

        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"

        old = user.uuid.hex
        user.uuid = new_uuid
        await session.commit()
        return True, f"UUID: {old} → {new_uuid.hex}"


def set_expire(name_or_uuid: str, until_text: str) -> tuple[bool, str]:
    """Установить дату окончания. until_text — 'dd.mm.YYYY HH:MM' или 'dd.mm.YYYY'."""
    return runtime.run(_set_expire(name_or_uuid, until_text))


async def _set_expire(name_or_uuid: str, until_text: str) -> tuple[bool, str]:
    until = parse_until(until_text)
    if until is None:
        return False, "Неверный формат даты. Ожидается «ДД.ММ.ГГГГ ЧЧ:ММ» или «ДД.ММ.ГГГГ»."

    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        user.sub_expires_at = until
        await session.commit()
        return True, f"{user.name}: дата окончания → {until:%d.%m.%Y %H:%M} UTC"


def toggle_flag(name_or_uuid: str, flag: str) -> tuple[bool, str]:
    """flag: 'vpn_user' | 'proxy_user' | 'ios_user'"""
    return runtime.run(_toggle_flag(name_or_uuid, flag))


async def _toggle_flag(name_or_uuid: str, flag: str) -> tuple[bool, str]:
    async with Session() as session:
        repo = UserRepository(session)
        user = await find_user(repo, name_or_uuid)
        if user is None:
            return False, "Пользователь не найден"
        new_value = not bool(getattr(user, flag))
        setattr(user, flag, new_value)
        await session.commit()
        return True, f"{user.name}: {flag} → {'да' if new_value else 'нет'}"
