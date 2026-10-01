from loguru import logger

from src.db.models import Users
from src.core.interfaces import Installer, Controller, Configurator
from src.infrastructure.system.subprocess import check_root
from src.infrastructure.system.systemctl import SystemdUnit, daemon_reload


class SystemdUnitInstaller(Installer):
    def __init__(self, service_name: str, service_file_content: str):
        self.__service = SystemdUnit(service_name)
        self.__service_file_content = service_file_content

    @property
    def is_installed(self) -> bool:
        return self.__service.exists()

    def _install(self):
        check_root()

        logger.info(f"Install {self.__service.name} service")
        self.__service.write_config(self.__service_file_content)
        daemon_reload()

    def _uninstall(self):
        check_root()

        logger.info(f"Uninstall {self.__service.name} service")
        self.__service.disable()
        self.__service.stop()
        self.__service.remove()
        daemon_reload()


class SystemdUnitConfigurator(Configurator):
    def __init__(self, service_name: str):
        self.__service = SystemdUnit(service_name)

    def apply(self, users: Users):
        self.__service.reload()


class SystemdUnitController(Controller):
    def __init__(self, service_name: str):
        self.__service = SystemdUnit(service_name)

    @property
    def status(self) -> bool:
        return self.__service.status()

    def start(self):
        self.__service.enable()
        self.__service.start()

    def stop(self):
        self.__service.disable()
        self.__service.stop()

    def restart(self):
        self.__service.enable()
        self.__service.restart()

    def reload(self):
        self.__service.reload()
