# ======================================================================
# Файл: src/cli/widgets/prompts.py
# ======================================================================
from typing import Any, Callable

import questionary
from questionary import Choice


__all__ = [
    "Choice",
    "select",
    "checkbox",
    "confirm",
    "text",
    "password",
    "pause",
]


def _safe(fn: Callable[[], Any]) -> Any:
    """Возвращает None при Ctrl+C/Esc вместо исключения."""
    try:
        return fn()
    except KeyboardInterrupt:
        return None


def select(
    message: str,
    choices: list[Any],
    default: Any | None = None,
) -> Any | None:
    kwargs: dict[str, Any] = {
        "message": message,
        "choices": choices,
        "qmark": "▸",
        "instruction": "(↑↓ — выбор, Enter — подтвердить)",
    }
    if default is not None:
        kwargs["default"] = default

    return _safe(lambda: questionary.select(**kwargs).ask())


def checkbox(
    message: str,
    choices: list[Any],
    default: list[Any] | None = None,
) -> list[Any] | None:
    kwargs: dict[str, Any] = {
        "message": message,
        "choices": choices,
        "qmark": "▸",
        "instruction": "(↑↓ — навигация, Space — выбор, Enter — подтвердить)",
    }
    # В questionary >=2.0 пустой default=[] ломает валидацию,
    # поэтому передаём его только если он непустой.
    if default:
        kwargs["default"] = default

    return _safe(lambda: questionary.checkbox(**kwargs).ask())


def confirm(message: str, default: bool = False) -> bool | None:
    return _safe(
        lambda: questionary.confirm(
            message,
            default=default,
            qmark="▸",
        ).ask()
    )


def text(
    message: str,
    default: str = "",
    validate: Callable[[str], bool | str] | None = None,
) -> str | None:
    return _safe(
        lambda: questionary.text(
            message,
            default=default,
            validate=validate or (lambda _: True),
            qmark="▸",
        ).ask()
    )


def password(
    message: str,
    validate: Callable[[str], bool | str] | None = None,
) -> str | None:
    return _safe(
        lambda: questionary.password(
            message,
            validate=validate or (lambda _: True),
            qmark="▸",
        ).ask()
    )


def pause(message: str = "Enter — назад") -> None:
    _safe(lambda: questionary.press_any_key_to_continue(message).ask())
