import argparse
import asyncio
import inspect
import sys

from core.backend import Backend
from core.commands import install_targets, uninstall_targets, apply_configuration, import_users_from_file, \
    print_user_info, set_user_expire, start_services, stop_services, restart_services, print_services_status
from database.connection import create_tables


# ============================================================
# Парсер
# ============================================================

def parse_targets(value: str) -> list[Backend]:
    backends = Backend.all()

    try:
        return [backends[item.strip()] for item in value.split(",") if item.strip()]
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Неизвестная цель. Доступные: {','.join(backends.keys())}"
        ) from e


def resolve_targets(targets: list[Backend]) -> list[Backend]:
    """Если targets пуст — вернуть только установленные цели."""
    if targets:
        return targets

    installed = Backend.installed()
    if not installed:
        raise SystemExit(
            "Не указаны цели и не найдено ни одного установленного сервиса. "
            f"Укажите --targets из списка: {','.join(Backend.all().keys())}"
        )
    return list(installed.values())


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
                f"Цели через запятую: {','.join(Backend.all().keys())}. "
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


async def handle_configure(args: argparse.Namespace) -> None:
    if args.configure_command == "apply":
        targets = resolve_targets(args.targets)
        await apply_configuration(targets)


async def handle_user(args: argparse.Namespace):
    cmd = args.user_command

    if cmd == "import":
        await import_users_from_file(args.file)
    elif cmd == "info":
        await print_user_info(args.name)
    elif cmd == "set-expire":
        await set_user_expire(args.name, args.until)


def handle_service(args: argparse.Namespace) -> None:
    cmd = args.service_command
    targets = resolve_targets(args.targets)

    action = {
        "start": start_services,
        "stop": stop_services,
        "restart": restart_services,
        "status": print_services_status
    }[cmd]

    action(targets)


# ============================================================
# main
# ============================================================

async def _run_async(handler, args: argparse.Namespace) -> None:
    await create_tables()
    await handler(args)


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

    handler = handlers[args.command]
    if inspect.iscoroutinefunction(handler):
        asyncio.run(_run_async(handler, args))
    else:
        handler(args)


if __name__ == "__main__":
    main(sys.argv[1:])
