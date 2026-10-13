import os
import shutil
import subprocess

from src.settings.app import BASE_DIR
from src.cli.console import console, err, info, warn


ENV_PATH = BASE_DIR / ".env"


def _find_editor() -> list[str] | None:
    """Возвращает команду редактора или None."""
    # Приоритет: $EDITOR, $VISUAL, vim, nano, vi
    for env_var in ("EDITOR", "VISUAL"):
        value = os.environ.get(env_var)
        if value:
            return value.split()

    for name in ("vim", "nano", "vi"):
        if shutil.which(name):
            return [name]

    return None


def edit_env() -> bool:
    """Открывает .env в редакторе. Возвращает True, если файл был открыт.

    Не проверяет, изменён ли файл — просто факт запуска редактора.
    """
    if not ENV_PATH.exists():
        err(f"Файл {ENV_PATH} не найден")
        return False

    cmd = _find_editor()
    if cmd is None:
        err("Не найден редактор. Установите vim/nano или задайте $EDITOR.")
        return False

    editor_name = " ".join(cmd)
    info(f"Открываю {ENV_PATH} в {editor_name}…")
    console.print("[dim]Сохраните и выйдите из редактора для продолжения.[/]")

    try:
        result = subprocess.run([*cmd, str(ENV_PATH)], check=False)
    except FileNotFoundError:
        err(f"Редактор {editor_name} не найден")
        return False
    except KeyboardInterrupt:
        # пользователь нажал Ctrl+C — редактор тоже завершится
        return False

    if result.returncode != 0:
        warn(f"Редактор завершился с кодом {result.returncode}")

    return True
