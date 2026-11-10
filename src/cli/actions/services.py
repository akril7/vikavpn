from src.application.ports.registry import RegistryLike
from src.application.ports.services import ControllerError
from src.application.services.orchestration import control
from src.cli.console import console, err, ok, warn
from src.cli.utils.root import require_root


def status(registry, names: list[str]) -> dict[str, bool]:
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
    registry: RegistryLike,
    names: list[str],
) -> bool:
    if not require_root(action_name):
        return False

    if not names:
        warn("Ничего не выбрано")
        return False

    ok_all = True
    for name in names:
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


def start(registry, names: list[str]) -> bool:
    return _run_action("запуск", control.start, registry, names)


def stop(registry, names: list[str]) -> bool:
    return _run_action("остановка", control.stop, registry, names)


def restart(registry, names: list[str]) -> bool:
    return _run_action("перезапуск", control.restart, registry, names)


def reload(registry, names: list[str]) -> bool:
    return _run_action("перезагрузка конфига", control.reload, registry, names)
