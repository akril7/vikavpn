from abc import ABC

from loguru import logger

from src.application.ports.services.callables import IsInstallCallback
from src.application.services import BaseInstaller, BaseConfigurator, BaseController
from src.infrastructure.system.subprocess import check_root
from src.infrastructure.system.systemctl import SystemdUnit, daemon_reload


class SystemdUnitInstaller(BaseInstaller):
    def __init__(self, service_name: str, service_file_content: str):
        self.__service = SystemdUnit(service_name)
        self.__service_file_content = service_file_content

    @property
    def is_installed(self) -> bool:
        return self.__service.exists()

    def _install(self):
        check_root()

        logger.debug(f"Install {self.__service.name} service")
        self.__service.write_config(self.__service_file_content)
        daemon_reload()

    def _uninstall(self):
        check_root()

        logger.debug(f"Uninstall {self.__service.name} service")
        self.__service.disable()
        self.__service.stop()
        self.__service.remove()
        daemon_reload()


class SystemdUnitConfigurator(BaseConfigurator, ABC):
    def __init__(self,
                 service_name: str,
                 is_install_callback: IsInstallCallback):
        service = SystemdUnit(service_name)
        super().__init__(is_install_callback, service.reload)


class SystemdUnitController(BaseController):
    def __init__(self, service_name: str, is_install_callback: IsInstallCallback):
        super().__init__(is_install_callback)
        self.__service = SystemdUnit(service_name)

    @property
    def _status(self) -> bool:
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

    def _reload(self):
        self.__service.reload()
