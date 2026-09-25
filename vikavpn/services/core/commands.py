import asyncio
import tomllib
from datetime import datetime, UTC

from loguru import logger
from uuid import UUID

from database.repo.management import UserManagementRepository
from database.repo.user import UserRepository
from settings import telegram_bot, tls, clash, mtproxyl, webserver
from settings.app import SNI
from services.backends.backend import Backend, CLASH_BACKEND
from database.connection import Session
from database.models import User
from services import url_build


def find_user_by_name(name: str, users: list[User]) -> User:
    for u in users:
        if u.name == name:
            return u
    raise RuntimeError(f"Пользователь '{name}' не найден")


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
        repo = UserRepository(session)
        users = await repo.list_active()

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

    logger.info("lol")

    async with Session() as session:
        user_repo = UserRepository(session)
        manage_repo = UserManagementRepository(session)

        for raw in users_data:
            logger.info(f"Load {raw["name"]}")
            user = await user_repo.create(
                name=raw["name"],
                password=raw["password"],
                sub_expires_at=datetime.strptime(raw["sub_expires"], "%Y-%m-%d").replace(tzinfo=UTC),
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
                await manage_repo.create(
                    manager=find_user_by_name(raw["name"], users),
                    managed=find_user_by_name(username, users),
                )
                user_managements_counter += 1

        logger.info("Commit")
        await session.commit()

    print(
        f"""Импорт завершён!
Пользователей: {len(users)}
Связей управления: {user_managements_counter}"""
    )


async def get_user_info(name: str) -> str:
    """Получить информацию о пользователе по имени."""
    async with Session() as session:
        repo = UserRepository(session)

        user = await repo.get_by_name(name)
        if not user:
            raise RuntimeError(f"Пользователь {name} не найден")

        user = await repo.get_with_managed_users(user.id)

        return (
            f"""Информация о пользователе:
    Имя: {user.name}
    Пароль: {user.password}
    UUID: {user.uuid}
    Активен: {user.is_active}
    Использует прокси: {user.proxy_user}
    Использует VPN: {user.vpn_user}
    Использует IOS: {user.ios_user}
    Управляет пользователями: {", ".join(muser.managed.name for muser in user.managed_links)}
    Подписка истекает: {user.sub_expires_at.strftime("%d.%m.%Y %H:%M")}

    Clash-ссылка
    {url_build.build_clash_config_url(user, webserver.server, clash.url_config_path) if user.vpn_user else ""}
    
    TG-прокси
    {url_build.build_telegram_proxy_url(user, SNI, tls.domain, mtproxyl.port) if user.proxy_user else ""}
    
    Ссылка для входа в бота:
    {url_build.build_bot_auth_url(telegram_bot.username, user)}
"""
        )


async def print_user_info(name: str):
    print(await get_user_info(name))


async def set_user_expire(name: str, until: str):
    """Установить срок окончания подписки."""
    async with Session() as session:
        repo = UserRepository(session)

        user = await repo.get_by_name(name)
        if not user:
            raise RuntimeError(f"Пользователь {name} не найден")

        user.sub_expires_at = datetime.strptime(until, "%Y-%m-%d")
        await session.commit()

    logger.info(f"{name}: срок подписки установлен на {user.sub_expires_at:%d.%m.%Y}")


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
    targets = list(Backend.endpoints().values())
    await apply_configuration(targets)
    await asyncio.to_thread(restart_services, targets)
