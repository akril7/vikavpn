import shutil
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from config.trusttunnel import TrustTunnelSettings
from services.base import Installer
from services.trusttunnel.render import render_service_config
from utils import check_root, download_file, unpack_clean
from utils.systemctl import SystemdService, daemon_reload

from config.app import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "trusttunnel"))


class TrustTunnelInstaller(Installer):
    def __init__(self, config: TrustTunnelSettings):
        self.__download_link = config.archive_download_link
        self.__install_dir = config.install_dir
        self.__service = SystemdService(config.service)

    @property
    def is_installed(self) -> bool:
        return self.__service.exists() and (self.__install_dir / "trusttunnel_endpoint").exists()

    def _install(self, force: bool = False):
        if self.is_installed and not force:
            logger.info("Trusttunnel already installed")
            return

        check_root()

        self.__install_dir.mkdir(parents=True, exist_ok=True)

        archive_path = self.__install_dir / Path(urlparse(self.__download_link).path).name

        logger.info("Get trusttunel archive")
        download_file(self.__download_link, archive_path)

        logger.info("Unpack trusttunel archive")
        unpack_clean(archive_path, self.__install_dir)

        logger.info("Create trusttunel service")
        self.__service.write_config(render_service_config(self.__install_dir))

    def _uninstall(self):
        check_root()

        if self.__install_dir.exists():
            if not (self.__install_dir / "trusttunnel_endpoint").exists():
                raise FileNotFoundError(f"{self.__install_dir} is not dir of trusttunnel")

            logger.info("Remove trusttunnel dir")
            shutil.rmtree(self.__install_dir)

        logger.info("Remove trusttunel service")
        self.__service.stop()
        self.__service.remove()
        daemon_reload()
