from src.cli.console import err, warn
from src.infrastructure.system.subprocess import is_root


def require_root(action: str) -> bool:
    if is_root():
        return True
    err(f"Требуются права root для операции «{action}».")
    warn("Запустите панель через sudo.")
    return False
