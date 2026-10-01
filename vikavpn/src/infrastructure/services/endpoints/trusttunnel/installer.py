import shutil
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

from src.settings.endpoints.trusttunnel import TrustTunnelSettings
from src.infrastructure.systemd import SystemdUnitInstaller
from src.infrastructure.system.subprocess import check_root
from src.core.utils.file import download_file

from .render import render_service


class TrustTunnelInstaller(SystemdUnitInstaller):
    def __init__(self, config: TrustTunnelSettings):
        super().__init__(config.service_name, render_service(str(config.install_dir)))

        self.__download_link = config.archive_download_link
        self.__install_dir = config.install_dir

    @property
    def is_installed(self) -> bool:
        return (self.__install_dir / "trusttunnel_endpoint").exists() and super().is_installed

    def _install(self):
        check_root()

        self.__install_dir.mkdir(parents=True, exist_ok=True)

        archive_path = self.__install_dir / Path(urlparse(self.__download_link).path).name

        logger.info(f"Get trusttunel archive")
        download_file(self.__download_link, archive_path)

        logger.info("Unpack trusttunel archive")
        shutil.unpack_archive(archive_path, self.__install_dir)
        # unpack_clean(archive_path, self.__install_dir)

        super()._install()

    def _uninstall(self):
        check_root()

        if self.__install_dir.exists():
            if not (self.__install_dir / "trusttunnel_endpoint").exists():
                raise FileNotFoundError(f"{self.__install_dir} is not dir of trusttunnel")

            logger.info("Remove trusttunnel dir")
            shutil.rmtree(self.__install_dir)

        super()._uninstall()
