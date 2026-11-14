from loguru import logger

from src.application.ports.registry import RegistryLike


def status(registry: RegistryLike, names: list[str]) -> dict[str, bool]:
    result = {}
    for name in names:
        target = registry.get_controller(name)
        logger.debug(f"Получение статуса для {name}")
        result[name] = target.status

    return result


def start(registry: RegistryLike, names: list[str]):
    for name in names:
        target = registry.get_controller(name)
        logger.debug(f"Запуск {name}")
        target.start()


def stop(registry: RegistryLike, names: list[str]):
    for name in names:
        target = registry.get_controller(name)
        logger.debug(f"Остановка {name}")
        target.stop()


def restart(registry: RegistryLike, names: list[str]):
    for name in names:
        target = registry.get_controller(name)
        logger.debug(f"Перезапуск {name}")
        target.restart()


def reload(registry: RegistryLike, names: list[str]):
    for name in names:
        target = registry.get_controller(name)
        logger.debug(f"Перезагрузка {name}")
        target.reload()
