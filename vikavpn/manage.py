import argparse
import inspect
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from loguru import logger

from config.app import TZ
from config.clash import ClashSettings
from config.hysteria import HysteriaSettings
from config.mita import MitaSettings
from config.mtproxyl import MTProxyLSettings
from config.ssl import TLSSettings
from config.trusttunnel import TrustTunnelSettings
from config.webserver import WebServerSettings
from database.connection import Session
from database.crud import (
    create_user,
    create_user_messager,
    create_user_management,
    get_user_by_name, get_active_users,
)
from database.models import User
from services.base import Installer, Configurator, Service, StubConfigurator, StubService
from services.clash_config import ClashConfigurator
from services.hysteria import HysteriaInstaller, HysteriaConfigurator, HysteriaService
from services.mita import MitaInstaller, MitaConfigurator, MitaService
from services.mtproxyl import MTProxyLInstaller, MTProxyLConfigurator, MTProxyLService
from services.trusttunnel import TrustTunnelInstaller, TrustTunnelConfigurator, TrustTunnelService
from services.webserver import WebServerInstaller


class Target(StrEnum):
    MITA = "mita"
    TRUSTTUNNEL = "trusttunnel"
    HYSTERIA = "hysteria"
    MTPROXYL = "mtproxyl"
    WEBSERVER = "webserver"


@dataclass
class TargetService:
    installer: Installer
    configurator: Configurator
    service: Service


tls_config = TLSSettings()
clash_config = ClashSettings()
mita_config = MitaSettings()
trusttunnel_config = TrustTunnelSettings()
hysteria_config = HysteriaSettings()
mtproxyl_config = MTProxyLSettings()
webserver_config = WebServerSettings()

clash_configurator = ClashConfigurator(clash_config, tls_config, mita_config, hysteria_config, trusttunnel_config)

TARGETS = {
    Target.MITA: TargetService(MitaInstaller(mita_config),
                               MitaConfigurator(mita_config),
                               MitaService(mita_config)),
    Target.TRUSTTUNNEL: TargetService(TrustTunnelInstaller(trusttunnel_config),
                                      TrustTunnelConfigurator(trusttunnel_config, tls_config),
                                      TrustTunnelService(trusttunnel_config)),
    Target.HYSTERIA: TargetService(HysteriaInstaller(hysteria_config, tls_config),
                                   HysteriaConfigurator(hysteria_config),
                                   HysteriaService(hysteria_config)),
    Target.MTPROXYL: TargetService(MTProxyLInstaller(mtproxyl_config, tls_config),
                                   MTProxyLConfigurator(mtproxyl_config),
                                   MTProxyLService()),
    Target.WEBSERVER: TargetService(WebServerInstaller(webserver_config, tls_config),
                                    StubConfigurator(),
                                    StubService()),
}


def find_user_by_name(name: str, users: list[User]) -> User:
    for u in users:
        if u.name == name:
            return u
    raise ValueError(f"Пользователь '{name}' не найден")


def installations() -> list[tuple[Target, Service, bool]]:
    """Для каждой цели: (target, service, установлен ли installer)."""
    return [
        (target, ts.service, ts.installer.is_installed)
        for target, ts in TARGETS.items()
    ]


def installed_targets() -> list[Target]:
    """Вернуть цели, у которых сервис установлен."""
    return [
        target
        for target, ts in TARGETS.items()
        if ts.installer.is_installed
    ]


# ============================================================
# Парсер
# ============================================================

def parse_targets(value: str) -> list[Target]:
    try:
        return [Target(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Неизвестная цель. Доступные: {','.join(Target)}"
        ) from e


def resolve_targets(targets: list[Target]) -> list[Target]:
    """Если targets пуст — вернуть только установленные цели."""
    if targets:
        return targets

    installed = installed_targets()
    if not installed:
        raise SystemExit(
            "Не указаны цели и не найдено ни одного установленного сервиса. "
            f"Укажите --targets из списка: {','.join(Target)}"
        )
    return installed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Управление сервисами VIKAVPN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  python3 manage.py install --targets=mita,webserver\n"
            "  python3 manage.py uninstall --targets=mtproxyl\n"
            "  python3 manage.py service start --targets=hysteria,mita\n"
            "  python3 manage.py service stop\n"
            "  python3 manage.py service restart --targets=hysteria,mita\n"
            "  python3 manage.py service status\n"
            "  python3 manage.py configure apply\n"
            "  python3 manage.py configure apply --targets=hysteria,mita\n"
            "  python3 manage.py user import --file users.toml\n"
            "  python3 manage.py user info --name alice\n"
            "  python3 manage.py user deactivate --name alice\n"
            "  python3 manage.py user activate --name alice\n"
            "  python3 manage.py user set-expire --name alice --until 2026-01-01\n"
        ),
    )

    def add_targets_arg(prs: argparse.ArgumentParser, required: bool = False):
        prs.add_argument(
            "--targets",
            type=parse_targets,
            default=[],
            required=required,
            metavar="СПИСОК",
            help=(
                f"Цели через запятую: {','.join(Target)}. "
                "Если не указано — берутся только установленные цели."
            ),
        )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- install / uninstall ----
    p = sub.add_parser("install", help="Установить цели")
    add_targets_arg(p, required=True)
    p.add_argument("--force", action="store_true", help="Установить принудительно")

    p = sub.add_parser("uninstall", help="Удалить цели")
    add_targets_arg(p, required=True)

    # ---- service ----
    service = sub.add_parser("service", help="Управление сервисами")
    service_sub = service.add_subparsers(dest="service_command", required=True)

    for cmd, helptext in (
        ("start", "Запустить сервисы"),
        ("stop", "Остановить сервисы"),
        ("restart", "Перезапустить сервисы"),
        ("status", "Показать статус сервисов"),
    ):
        p_srv = service_sub.add_parser(cmd, help=helptext)
        add_targets_arg(p_srv, required=False)

    # ---- configure ----
    configure = sub.add_parser("configure", help="Управление конфигурацией")
    configure_sub = configure.add_subparsers(dest="configure_command", required=True)

    p_apply = configure_sub.add_parser(
        "apply",
        help="Применить конфигурацию к пользователям",
    )
    add_targets_arg(p_apply, required=False)

    # ---- user ----
    user = sub.add_parser("user", help="Управление пользователями")
    user_sub = user.add_subparsers(dest="user_command", required=True)

    p_import = user_sub.add_parser("import", help="Импорт пользователей из файла TOML")
    p_import.add_argument("--file", required=True, help="Путь к файлу с пользователями")

    p_info = user_sub.add_parser("info", help="Информация о пользователе")
    p_info.add_argument("--name", required=True, help="Имя пользователя")

    p_deact = user_sub.add_parser("deactivate", help="Деактивировать пользователя")
    p_deact.add_argument("--name", required=True, help="Имя пользователя")

    p_act = user_sub.add_parser("activate", help="Активировать пользователя")
    p_act.add_argument("--name", required=True, help="Имя пользователя")

    p_exp = user_sub.add_parser("set-expire", help="Установить срок подписки")
    p_exp.add_argument("--name", required=True, help="Имя пользователя")
    p_exp.add_argument(
        "--until",
        required=True,
        help="Дата окончания (например, 2026-01-01)",
    )

    return parser


# ============================================================
# Обработчики команд
# ============================================================

def handle_install(args: argparse.Namespace):
    install_targets(args.targets, args.force)


def handle_uninstall(args: argparse.Namespace):
    uninstall_targets(args.targets)


def handle_configure(args: argparse.Namespace) -> None:
    if args.configure_command == "apply":
        targets = resolve_targets(args.targets)
        apply_configuration(targets)


def handle_user(args: argparse.Namespace):
    cmd = args.user_command

    if cmd == "import":
        import_users_from_file(args.file)
    elif cmd == "info":
        print_user_info(args.name)
    elif cmd == "deactivate":
        set_user_enabled(args.name, False)
    elif cmd == "activate":
        set_user_enabled(args.name, True)
    elif cmd == "set-expire":
        set_user_expire(args.name, args.until)


def handle_service(args: argparse.Namespace) -> None:
    cmd = args.service_command
    targets = resolve_targets(args.targets)

    action = {
        "start": start_services,
        "stop": stop_services,
        "restart": restart_services,
        "status": print_services_status,
    }[cmd]

    action(targets)


# ============================================================
# Команды
# ============================================================

def install_targets(targets: list[Target], force: bool):
    """Установить указанные сервисы."""
    for target in targets:
        ts = TARGETS[target]

        if ts.installer.is_installed and not force:
            logger.info(f"{target}: уже установлен, пропускаем (используйте --force)")
            continue

        installer = ts.installer
        sig = inspect.signature(installer.install)
        if "force" in sig.parameters:
            installer.install(force=force)
        else:
            installer.install()


def uninstall_targets(targets: list[Target]):
    """Удалить указанные сервисы."""
    for target in targets:
        ts = TARGETS[target]
        if not ts.installer.is_installed:
            logger.info(f"{target}: не установлен, пропускаем")
            continue
        ts.installer.uninstall()


def apply_configuration(targets: list[Target]) -> None:
    with Session() as session:
        users = get_active_users(session)

    logger.info(f"Пользователей для применения: {len(users)}")

    for target in targets:
        ts = TARGETS[target]
        if not ts.installer.is_installed:
            logger.warning(f"{target}: не установлен, пропускаем")
            continue

        logger.info(f"{target}: применяем конфигурацию...")
        ts.configurator.apply(users)
        logger.info(f"{target}: конфигурация применена")

    logger.info("Сохранение clash-конфигов")
    clash_configurator.apply(users)


def import_users_from_file(path: str):
    """Импорт пользователей из файла."""
    with open(path, 'rb') as f:
        data = tomllib.load(f)

    users_data = data.get("users", [])

    user_msgr_counter = 0
    user_managements_counter = 0

    users = []

    with Session() as session:
        for raw in users_data:
            user = create_user(
                session=session,
                name=raw["name"],
                password=raw["password"],
                sub_expires_at=datetime.strptime(raw["sub_expires"], "%Y-%m-%d"),
                uuid=UUID(raw["uuid"]),
                vpn_user=raw.get("use_vpn", True),
                proxy_user=raw.get("use_proxy", True),
                ios_user=raw.get("use_ios", False),
                enabled=raw.get("active", True)
            )
            users.append(user)

            tg_id = raw.get("telegram_id")
            vk_id = raw.get("vk_id")
            if tg_id or vk_id:
                create_user_messager(
                    session=session,
                    user=user,
                    telegram_id=tg_id,
                    vk_id=vk_id
                )
                user_msgr_counter += 1

        for raw in users_data:
            managed_users = raw.get("managed_users")
            if not managed_users:
                continue

            for username in managed_users:
                create_user_management(
                    session=session,
                    manager=find_user_by_name(raw["name"], users),
                    managed=find_user_by_name(username, users)
                )
                user_managements_counter += 1

    print(f"""Импорт завершён!
Пользователей: {len(users)}
Связей с мессенджерами: {user_msgr_counter}
Связей управления: {user_managements_counter}""")


def get_user_info(name: str) -> str:
    """Получить информацию о пользователе по имени."""
    with Session() as session:
        user = get_user_by_name(session, name)
        return (f"""Информация о пользователе:
    Имя: {user.name}
    Пароль: {user.password}
    UUID: {user.uuid}
    Активен: {user.enabled}
    Использует прокси: {user.proxy_user}
    Использует VPN: {user.vpn_user}
    Использует IOS: {user.ios_user}
    Telegram ID: {user.messager.telegram_id if user.messager else "Не задано"}
    VK ID: {user.messager.vk_id if user.messager else "Не задано"}
    Управляет пользователями: {", ".join(managed_user.name for managed_user in user.managed_users)}
    Подписка истекает: {user.sub_expires_at.strftime("%d.%m.%Y %H:%M")}""")


def print_user_info(name: str):
    print(get_user_info(name))


def set_user_enabled(name: str, enabled: bool):
    """Активировать или деактивировать пользователя."""
    with Session() as session:
        user = get_user_by_name(session, name)
        user.enabled = enabled
        session.commit()
    logger.info(f"{name}: {'активирован' if enabled else 'деактивирован'}")


def set_user_expire(name: str, until: str):
    """Установить срок окончания подписки."""
    with Session() as session:
        user = get_user_by_name(session, name)
        user.sub_expires_at = datetime.strptime(until, "%Y-%m-%d")
        if user.sub_expires_at < datetime.now(tz=TZ):
            user.enabled = False
        session.commit()
    logger.info(f"{name}: срок подписки установлен на {user.sub_expires_at:%d.%m.%Y}")


def get_services_status(targets: list[Target]) -> str:
    """Получить статус сервисов (установлен + запущен)."""
    lines = []

    states = {
        target: (service, installed)
        for target, service, installed in installations()
    }

    for target in targets:
        service, installed = states[target]
        installed_str = "установлен" if installed else "не установлен"

        if not installed:
            lines.append(f"{target}: {installed_str}")
            continue

        try:
            running = service.status
            running_str = "запущен" if running else "остановлен"
        except Exception as e:
            running_str = f"ошибка проверки ({e})"

        lines.append(f"{target}: {installed_str}, {running_str}")

    return "\n".join(lines)


def print_services_status(targets: list[Target]):
    print(get_services_status(targets=targets))


def start_services(targets: list[Target]) -> None:
    """Запустить сервисы."""
    for target in targets:
        logger.info(f"{target}: запуск...")
        TARGETS[target].service.start()
        logger.info(f"{target}: запущен")


def stop_services(targets: list[Target]) -> None:
    """Остановить сервисы."""
    for target in targets:
        logger.info(f"{target}: остановка...")
        TARGETS[target].service.stop()
        logger.info(f"{target}: остановлен")


def restart_services(targets: list[Target]) -> None:
    """Перезапустить сервисы."""
    for target in targets:
        logger.info(f"{target}: перезапуск...")
        TARGETS[target].service.restart()
        logger.info(f"{target}: перезапущен")


# ============================================================
# main
# ============================================================

def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "install": handle_install,
        "uninstall": handle_uninstall,
        "service": handle_service,
        "configure": handle_configure,
        "user": handle_user,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main(sys.argv[1:])
