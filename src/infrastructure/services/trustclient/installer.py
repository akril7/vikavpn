import shutil
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

from src.core.utils.file import download_file, unpack_clean
from src.infrastructure.services.trustclient.render import render_service, render_config
from src.infrastructure.systemd import SystemdUnitInstaller
from src.settings.trustclient import TrustClientSettings


class TrustClientInstaller(SystemdUnitInstaller):
    def __init__(self, settings: TrustClientSettings):
        super().__init__(settings.service_name, render_service(str(settings.install_dir)))

        self.__install_dir = settings.install_dir
        self.__download_link = settings.archive_download_link
        self.__hostname = settings.hostname
        self.__port = settings.port
        self.__username = settings.username
        self.__password = settings.password
        self.__use_http2_proto = settings.use_http2_proto
        self.__socks5_address = settings.socks5_address

        if not all((self.__hostname, self.__port, self.__username, self.__password)):
            raise ValueError("TrustClientSettings not filled in env")

    @property
    def is_installed(self) -> bool:
        return (self.__install_dir / "trusttunnel_client").exists() and super().is_installed

    def _install(self):
        self.__install_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.__install_dir / Path(urlparse(self.__download_link).path).name

        logger.debug(f"Get trustclient archive")
        download_file(self.__download_link, archive_path)

        logger.debug("Unpack trustclient archive")
        unpack_clean(archive_path, self.__install_dir)

        config = render_config(
            hostname=self.__hostname,
            port=self.__port,
            username=self.__username,
            password=self.__password,
            use_http2_proto=self.__use_http2_proto,
            socks5_address=self.__socks5_address
        )

        (self.__install_dir / "config.toml").write_text(config)

        super()._install()

    def _uninstall(self):
        if self.__install_dir.exists():
            if not (self.__install_dir / "trusttunnel_client").exists():
                raise FileNotFoundError(f"{self.__install_dir} is not dir of trustclient")

            logger.debug("Remove trustclient dir")
            shutil.rmtree(self.__install_dir)

        super()._uninstall()
