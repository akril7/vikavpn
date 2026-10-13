from loguru import logger

from src.core.interfaces import Installer
from src.settings import Settings
from .auth.installer import HysteriaAuthInstaller
from .endpoint.installer import HysteriaEndpointInstaller


class HysteriaInstaller(Installer):
    def __init__(self, settings: Settings):
        self.__endpoint = HysteriaEndpointInstaller(settings.hysteria,
                                                    settings.tls,
                                                    settings.site)
        self.__auth = HysteriaAuthInstaller(settings.hysteria)

    @property
    def is_installed(self) -> bool:
        return self.__endpoint.is_installed and self.__auth.is_installed

    def _install(self):
        logger.info("Installing hysteria endpoint")
        self.__endpoint.install()
        logger.info("Installing hysteria auth")
        self.__auth.install()

    def _uninstall(self):
        logger.info("Uninstalling hysteria auth")
        self.__auth.uninstall()
        logger.info("Uninstalling hysteria endpoint")
        self.__endpoint.uninstall()
