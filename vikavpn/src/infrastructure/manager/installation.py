from loguru import logger

from .registry import Registry


def install(registry: Registry, by_names: list[str] | None = None):
    for name, target in registry.get_install_targets(by_names).items():
        if not target.is_installed:
            logger.info(f"Устанавливаем {name}")
            target.install()
        else:
            logger.warning(f"{name} уже установлен")


def uninstall(registry: Registry, by_names: list[str] | None = None):
    for name, target in registry.get_install_targets(by_names).items():
        if target.is_installed:
            logger.info(f"Удаляем {name}")
            target.uninstall()
        else:
            logger.warning(f"{name} не установлен")
