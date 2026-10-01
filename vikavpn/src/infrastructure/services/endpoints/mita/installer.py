import shutil
from pathlib import Path

from loguru import logger

from src.core.utils.file import download_file
from src.core.interfaces import Installer
from src.infrastructure.system.subprocess import deb_is_installed, check_root, install_deb, add_user_to_group, \
    uninstall_deb
from src.infrastructure.system.systemctl import SystemdUnit
from src.settings import MitaSettings

DEB_STORE_PATH = Path("/tmp/mita.deb")


class MitaInstaller(Installer):
    def __init__(self, config: MitaSettings):
        self.__package_download_link = config.package_download_link
        self.__service = SystemdUnit(config.service_name)

    @property
    def is_installed(self) -> bool:
        return deb_is_installed("mita")

    def _install(self):
        check_root()

        logger.info("Get mita package")
        download_file(self.__package_download_link, DEB_STORE_PATH)

        logger.info("Install package")
        install_deb(str(DEB_STORE_PATH))

        logger.info("Add user to mita group")
        add_user_to_group("root", "mita")

    def _uninstall(self):
        check_root()

        logger.info("Delete mita package")
        uninstall_deb("mita")

        logger.info("Delete mita configuration")
        shutil.rmtree("/etc/mita")
