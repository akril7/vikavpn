from loguru import logger

from src.application.ports.registry import RegistryLike


def install(registry: RegistryLike, names: list[str]):
    """ Установить цели по их name """

    for name in names:
        target = registry.get_installer(name)
        if not target.is_installed:
            logger.debug(f"Устанавливаем {name}")
            target.install()
        else:
            logger.warning(f"{name} уже установлен")


def uninstall(registry: RegistryLike, names: list[str]):
    """ Удалить цели по их name """
    for name in names:
        target = registry.get_installer(name)
        if target.is_installed:
            logger.debug(f"Удаляем {name}")
            target.uninstall()
        else:
            logger.warning(f"{name} не установлен")


def get_installed(registry: RegistryLike, names: list[str] | None = None) -> dict[str, bool]:
    """ Установлена ли каждая из целей """
    if names is None:
        names = registry.names_of_installers

    return {
        name: registry.get_installer(name).is_installed for name in names
    }


def filter_installed_names(registry: RegistryLike, target: list[str]) -> list[str]:
    installed = get_installed(registry)
    return [
        name for name in target
        if name not in installed or installed.get(name, False)
    ]
