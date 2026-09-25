from loguru import logger

from services.backends.base import Installer, Service
from services.system.subprocess import check_root
from services.system.systemctl import SystemdDaemon, daemon_reload


class SystemdInstaller(Installer):
    def __init__(self, service_name: str, service_file_content: str):
        self.__service = SystemdDaemon(service_name)
        self.__service_file_content = service_file_content

    @property
    def is_installed(self) -> bool:
        return self.__service.exists()

    def _install(self, force: bool = False):
        if self.is_installed and not force:
            logger.info(f"Daemon {self.__service.name} already installed")
            return

        check_root()

        self.__service.write_config(self.__service_file_content)

    def _uninstall(self):
        check_root()

        self.__service.stop()
        self.__service.remove()
        daemon_reload()


class SystemdService(Service):
    def __init__(self, service_name: str):
        self.__service = SystemdDaemon(service_name)

    @property
    def status(self) -> bool:
        return self.__service.exists() and self.__service.status()

    def start(self):
        self.__service.enable()
        self.__service.start()

    def stop(self):
        self.__service.disable()
        self.__service.stop()

    def restart(self):
        self.__service.restart()
