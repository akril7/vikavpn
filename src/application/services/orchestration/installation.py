from loguru import logger

from src.application.ports.registry import RegistryLike


def install(registry: RegistryLike, names: list[str]):
    """ Установить цели по их name """

    for name in names:
        target = registry.get_installer(name)
        if not target.is_installed:
            logger.info(f"Устанавливаем {name}")
            target.install()
        else:
            logger.warning(f"{name} уже установлен")


def uninstall(registry: RegistryLike, names: list[str]):
    """ Удалить цели по их name """
    for name in names:
        target = registry.get_installer(name)
        if target.is_installed:
            logger.info(f"Удаляем {name}")
            target.uninstall()
        else:
            logger.warning(f"{name} не установлен")


def get_installed(registry: RegistryLike, names: list[str] | None = None) -> list[str]:
    """ Получить имена установленных целей """
    if names is None:
        names = registry.get_names_of_installers()

    return [
        name for name in names
        if registry.get_installer(name).is_installed
    ]
