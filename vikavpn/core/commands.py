import tomllib
from datetime import datetime

from loguru import logger
from uuid import UUID

from config import telegram_bot
from config.app import SNI
from core.backend import Backend, CLASH_BACKEND, clash, tls, mtproxyl
from database.connection import Session
from database.crud import get_active_users, create_user, create_user_management, \
    UserNotFoundError, get_user_by_name, get_expired_users
from database.models import User
from services import link


def find_user_by_name(name: str, users: list[User]) -> User:
    for u in users:
        if u.name == name:
            return u
    raise UserNotFoundError(f"Пользователь '{name}' не найден")


def install_targets(targets: list[Backend], force: bool):
    """Установить указанные сервисы."""
    for target in targets:
        target.install(force=force)


def uninstall_targets(targets: list[Backend]):
    """Удалить указанные сервисы."""
    for target in targets:
        target.uninstall()


async def apply_configuration(targets: list[Backend]) -> None:
    async with Session() as session:
        users = await get_active_users(session)

    logger.info(f"Пользователей для применения: {len(users)}")

    for target in targets:
        target.apply_config(users)

    if CLASH_BACKEND not in targets:
        CLASH_BACKEND.apply_config(users)


async def import_users_from_file(path: str):
    """Импорт пользователей из файла."""
    with open(path, "rb") as f:
        data = tomllib.load(f)

    users_data = data.get("users", [])

    user_managements_counter = 0

    users: list[User] = []

    async with Session() as session:
        for raw in users_data:
            user = await create_user(
                session=session,
                name=raw["name"],
                password=raw["password"],
                sub_expires_at=datetime.strptime(raw["sub_expires"], "%Y-%m-%d"),
                uuid=UUID(raw["uuid"]),
                vpn_user=raw.get("use_vpn", True),
                proxy_user=raw.get("use_proxy", True),
                ios_user=raw.get("use_ios", False),
            )
            users.append(user)

        for raw in users_data:
            managed_users = raw.get("managed_users")
            if not managed_users:
                continue

            for username in managed_users:
                await create_user_management(
                    session=session,
                    manager=find_user_by_name(raw["name"], users),
                    managed=find_user_by_name(username, users),
                )
                user_managements_counter += 1

    print(
        f"""Импорт завершён!
Пользователей: {len(users)}
Связей управления: {user_managements_counter}"""
    )


async def get_user_info(name: str) -> str:
    """Получить информацию о пользователе по имени."""
    async with Session() as session:
        user = await get_user_by_name(session, name)
        if not user:
            raise UserNotFoundError(f"{name}")

        return (
            f"""Информация о пользователе:
    Имя: {user.name}
    Пароль: {user.password}
    UUID: {user.uuid}
    Активен: {user.is_active}
    Использует прокси: {user.proxy_user}
    Использует VPN: {user.vpn_user}
    Использует IOS: {user.ios_user}
    Управляет пользователями: {", ".join(managed_user.name for managed_user in user.managed_users)}
    Подписка истекает: {user.sub_expires_at.strftime("%d.%m.%Y %H:%M")}

    Clash-ссылка
    {link.build_clash_config_url(user, tls.domain, clash.url_config_path)}
    
    TG-прокси
    {link.build_telegram_proxy_url(user, SNI, tls.domain, mtproxyl.port)}
    
    Ссылка для входа в бота:
    {link.build_bot_auth_url(telegram_bot.username, user)}
"""
        )


async def print_user_info(name: str):
    print(await get_user_info(name))


async def set_user_expire(name: str, until: str):
    """Установить срок окончания подписки."""
    async with Session() as session:
        user = await get_user_by_name(session, name)
        if not user:
            raise UserNotFoundError(f"{name}")

        user.sub_expires_at = datetime.strptime(until, "%Y-%m-%d")

        await session.commit()
    logger.info(
        f"{name}: срок подписки установлен на {user.sub_expires_at:%d.%m.%Y}"
    )


def get_services_status(targets: list[Backend]) -> str:
    """Получить статус сервисов (установлен + запущен)."""
    lines = []
    for target in targets:
        states = []

        if target.installer:
            states.append("установлен" if target.is_installed else "не установлен")
        else:
            states.append("-")

        if target.service:
            states.append("запущен" if target.service.status else "остановлен")
        else:
            states.append("-")

        lines.append(f"{target.name}: {', '.join(states)}")

    return "\n".join(lines)


def print_services_status(targets: list[Backend]):
    print(get_services_status(targets=targets))


def start_services(targets: list[Backend]) -> None:
    """Запустить сервисы."""
    for target in targets:
        if target.service:
            logger.info(f"{target.name}: запуск")
            target.service.start()
        else:
            logger.warning(f"{target.name}: запуск не поддерживается")


def stop_services(targets: list[Backend]) -> None:
    """Остановить сервисы."""
    for target in targets:
        if target.service:
            logger.info(f"{target.name}: остановка")
            target.service.stop()
        else:
            logger.warning(f"{target.name}: остановка не поддерживается")


def restart_services(targets: list[Backend]) -> None:
    """Перезапустить сервисы."""
    for target in targets:
        if target.is_installed and target.service:
            logger.info(f"{target.name}: перезапуск")
            target.service.restart()
        else:
            logger.warning(f"{target.name}: перезапуск не поддерживается")


async def reload_users():
    targets = list(Backend.installed().values())
    await apply_configuration(targets)
    restart_services(targets)
