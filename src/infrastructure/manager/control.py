from loguru import logger

from .registry import Registry


def status(registry: Registry, by_names: list[str] | None) -> dict[str, bool]:
    result = {}
    for name, target in registry.get_control_targets(by_names).items():
        logger.info(f"Получение статуса для {name}")
        result[name] = target.status

    return result


def start(registry: Registry, by_names: list[str] | None):
    for name, target in registry.get_control_targets(by_names).items():
        logger.info(f"Запуск {name}")
        target.start()


def stop(registry: Registry, by_names: list[str] | None):
    for name, target in registry.get_control_targets(by_names).items():
        logger.info(f"Остановка {name}")
        target.stop()


def restart(registry: Registry, by_names: list[str] | None):
    for name, target in registry.get_control_targets(by_names).items():
        logger.info(f"Перезапуск {name}")
        target.restart()


def reload(registry: Registry, by_names: list[str] | None):
    for name, target in registry.get_control_targets(by_names).items():
        logger.info(f"Перезагрузка {name}")
        target.reload()
