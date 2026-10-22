from src.core.interfaces import ControllerError
from src.infrastructure.manager import control
from src.infrastructure.system.subprocess import is_root
from src.cli.console import console, err, ok, warn


def _require_root(action: str) -> bool:
    if is_root():
        return True
    err(f"Требуются права root для операции «{action}».")
    warn("Запустите панель через sudo.")
    return False


def status(registry, names: list[str] | None = None) -> dict[str, bool]:
    """Возвращает {имя: is_up}. Без root тоже работает (systemctl status)."""
    try:
        return control.status(registry, names)
    except ControllerError as exc:
        err(f"Не удалось получить статус: {exc}")
        return {}
    except Exception as exc:  # noqa: BLE001
        err(f"Ошибка при получении статуса: {exc}")
        return {}


def _run_action(
    action_name: str,
    action_fn,
    registry,
    names: list[str] | None,
) -> bool:
    if not _require_root(action_name):
        return False

    targets = list(registry.get_control_targets(names).keys())

    if not targets:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in targets:
        with console.status(f"[cyan]{action_name}: {name}…[/]"):
            try:
                action_fn(registry, [name])
                ok(f"{name}: {action_name} — готово")
            except ControllerError as exc:
                err(f"{name}: {exc}")
                ok_all = False
            except Exception as exc:  # noqa: BLE001
                err(f"{name}: {exc}")
                ok_all = False
    return ok_all


def start(registry, names: list[str] | None = None) -> bool:
    return _run_action("запуск", control.start, registry, names)


def stop(registry, names: list[str] | None = None) -> bool:
    return _run_action("остановка", control.stop, registry, names)


def restart(registry, names: list[str] | None = None) -> bool:
    return _run_action("перезапуск", control.restart, registry, names)


def reload(registry, names: list[str] | None = None) -> bool:
    return _run_action("перезагрузка конфига", control.reload, registry, names)
