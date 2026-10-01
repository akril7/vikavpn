import argparse
import asyncio
import inspect
import sys

from src.db.connection import create_tables, Session
from src.db.repo import UserRepository
from src.infrastructure.manager import installation, control, configure
from src.infrastructure.manager.registry import Registry
from src.settings import Settings
from src.users.importer import import_users_from_file
from src.users.info import get_user_info
from src.users.subscription import set_expire


# ============================================================
# Парсер
# ============================================================

def parse_targets(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Управление сервисами VIKAVPN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  python3 manage.py setup\n"
            "  python3 manage.py install mita,webserver\n"
            "  python3 manage.py uninstall mtproxyl\n"
            "  python3 manage.py service start hysteria,mita\n"
            "  python3 manage.py service stop\n"
            "  python3 manage.py service restart hysteria,mita\n"
            "  python3 manage.py service status\n"
            "  python3 manage.py configure apply\n"
            "  python3 manage.py configure apply hysteria,mita\n"
            "  python3 manage.py user import users.toml\n"
            "  python3 manage.py user info alice\n"
            "  python3 manage.py user set-expire alice 2026-01-01\n"
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
                "Цели через запятую. "
                "Если не указано — берутся все."
            ),
        )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- setup ----
    sub.add_parser("setup", help="Установить и запустить все сервисы")

    # ---- install / uninstall ----
    p = sub.add_parser("install", help="Установить цели")
    add_targets_arg(p, required=False)

    p = sub.add_parser("uninstall", help="Удалить цели")
    add_targets_arg(p, required=False)

    # ---- service ----
    service = sub.add_parser("service", help="Управление сервисами")
    service_sub = service.add_subparsers(dest="service_command", required=True)

    for cmd, helptext in (
            ("start", "Запустить сервисы"),
            ("stop", "Остановить сервисы"),
            ("restart", "Перезапустить сервисы"),
            ("status", "Показать статус сервисов"),
            ("reload", "Перезагрузить конфиги сервисов"),
    ):
        p_srv = service_sub.add_parser(cmd, help=helptext)
        add_targets_arg(p_srv, required=False)

    # ---- configure ----
    configure_parser = sub.add_parser("configure", help="Управление конфигурацией")
    configure_sub = configure_parser.add_subparsers(dest="configure_command", required=True)

    p_apply = configure_sub.add_parser(
        "apply",
        help="Применить конфигурацию к пользователям",
    )
    add_targets_arg(p_apply, required=False)

    # ---- user ----
    user = sub.add_parser("user", help="Управление пользователями")
    user_sub = user.add_subparsers(dest="user_command", required=True)

    p_import = user_sub.add_parser("import", help="Импорт пользователей из файла TOML")
    p_import.add_argument("file", help="Путь к файлу с пользователями")

    p_info = user_sub.add_parser("info", help="Информация о пользователе")
    p_info.add_argument("name", help="Имя пользователя")

    p_exp = user_sub.add_parser("set-expire", help="Установить срок подписки")
    p_exp.add_argument("name", help="Имя пользователя")
    p_exp.add_argument("until", help="Дата окончания по UTC (например, 2026-01-01)")

    return parser


# ============================================================
# Обработчики команд
# ============================================================

async def handle_setup(_: argparse.Namespace, registry: Registry):
    await asyncio.to_thread(installation.uninstall, registry, None)
    await asyncio.to_thread(installation.install, registry, None)

    await configure.apply_active_users(registry)

    await asyncio.to_thread(control.restart, registry, None)


def handle_install(args: argparse.Namespace, registry: Registry):
    installation.install(registry, args.targets or None)


def handle_uninstall(args: argparse.Namespace, registry: Registry):
    installation.uninstall(registry, args.targets or None)


def handle_service(args: argparse.Namespace, registry: Registry):
    cmd = args.service_command
    names = args.targets or None

    action = {
        "start": control.start,
        "stop": control.stop,
        "restart": control.restart,
        "status": _print_status,
        "reload": control.reload,
    }[cmd]

    action(registry, names)


def _print_status(registry: Registry, names: list[str] | None):
    result = control.status(registry, names)
    for name, is_up in result.items():
        print(f"{name}: {'запущен' if is_up else 'остановлен'}")


async def handle_configure(args: argparse.Namespace, registry: Registry):
    if args.configure_command == "apply":
        await configure.apply_active_users(registry, args.targets or None)


async def handle_user(args: argparse.Namespace, registry: Registry):
    cmd = args.user_command

    if cmd == "import":
        count = await import_users_from_file(args.file)
        print(f"Импортировано пользователей: {count}")
    elif cmd == "info":
        print(await get_user_info(args.name, registry.settings))
    elif cmd == "set-expire":
        await _set_expire(args.name, args.until)


async def _set_expire(name: str, until: str):
    async with Session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_name(name)
        if user is None:
            raise RuntimeError(f"Пользователь {name} не найден")
        await set_expire(user, until)
        await session.commit()
    print(f"{name}: подписка истекает {user.sub_expires_at:%d.%m.%Y} (UTC)")


# ============================================================
# main
# ============================================================

async def _run_async(handler, args: argparse.Namespace, registry: Registry):
    await create_tables()
    await handler(args, registry)


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = Settings()
    registry = Registry(settings)

    handlers = {
        "setup": handle_setup,
        "install": handle_install,
        "uninstall": handle_uninstall,
        "service": handle_service,
        "configure": handle_configure,
        "user": handle_user,
    }

    handler = handlers[args.command]
    if inspect.iscoroutinefunction(handler):
        asyncio.run(_run_async(handler, args, registry))
    else:
        handler(args, registry)


if __name__ == "__main__":
    main(sys.argv[1:])
