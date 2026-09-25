import shutil
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

from settings.trusttunnel import TrustTunnelSettings
from services.backends.systemd import SystemdInstaller
from services.backends.trusttunnel.render import render_service
from services.system.subprocess import check_root
from utils.file import download_file, unpack_clean


class TrustTunnelInstaller(SystemdInstaller):
    def __init__(self, config: TrustTunnelSettings):
        super().__init__(config.service, render_service(str(config.install_dir)))

        self.__download_link = config.archive_download_link
        self.__install_dir = config.install_dir

    @property
    def is_installed(self) -> bool:
        return (self.__install_dir / "trusttunnel_endpoint").exists() and super().is_installed

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

        super()._install(force=force)

    def _uninstall(self):
        check_root()

        if self.__install_dir.exists():
            if not (self.__install_dir / "trusttunnel_endpoint").exists():
                raise FileNotFoundError(f"{self.__install_dir} is not dir of trusttunnel")

            logger.info("Remove trusttunnel dir")
            shutil.rmtree(self.__install_dir)

        super()._uninstall()
