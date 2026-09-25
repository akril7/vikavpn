import shutil
from pathlib import Path

from loguru import logger

from settings.mita import MitaSettings
from services.backends.base import Installer
from services.system.subprocess import is_installed, install_deb, add_user_to_group, uninstall_deb, check_root
from services.system.systemctl import SystemdDaemon
from utils.file import download_file

DEB_STORE_PATH = Path("/tmp/mita.deb")


class MitaInstaller(Installer):
    def __init__(self, config: MitaSettings):
        self.__package_download_link = config.package_download_link
        self.__service = SystemdDaemon(config.service)

    @property
    def is_installed(self) -> bool:
        return is_installed("mita")

    def _install(self, force: bool = False):
        check_root()

        logger.info("Get mita package")
        download_file(self.__package_download_link, DEB_STORE_PATH)

        logger.info("Install package")
        install_deb(str(DEB_STORE_PATH))

        logger.info("Add user to mita group")
        add_user_to_group("root", "mita")

    def _uninstall(self):
        if not self.is_installed:
            logger.info("Mita installation not found")
            return

        check_root()

        logger.info("Delete mita package")
        uninstall_deb("mita")

        logger.info("Delete mita configuration")
        shutil.rmtree("/etc/mita")
