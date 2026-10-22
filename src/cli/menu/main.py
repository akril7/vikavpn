from src.cli.widgets import prompts
from src.cli.widgets.prompts import Choice

MENU_ITEMS: list[tuple[str, str]] = [
    ("components", "Компоненты"),
    ("configure", "Конфигурация"),
    ("services", "Сервисы"),
    ("users", "Пользователи"),
    ("exit", "Выход"),
]


def main_menu() -> str | None:
    choices = [
        Choice(title=label, value=key)
        for key, label in MENU_ITEMS
    ]
    return prompts.select("Выберите раздел", choices=choices)
