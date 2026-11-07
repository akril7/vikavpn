import shutil
from pathlib import Path

from loguru import logger

from src.application.services import BaseInstaller
from src.configuration.app import DOWNLOAD_DIR
from src.infrastructure.system.subprocess import deb_is_installed, check_root, install_deb, uninstall_deb
from src.infrastructure.utils.file import download_file
from src.configuration import MihomoSettings, TLSSettings

from .render import render_config


class MihomoInstaller(BaseInstaller):
    def __init__(self, settings: MihomoSettings, tls: TLSSettings):
        self.__download_url = settings.download_url
        self.__hostname = settings.hostname
        self.__port = settings.port
        self.__username = settings.username
        self.__password = settings.password
        self.__use_quic = settings.use_quic
        self.__proxy_port = settings.proxy_port
        self.__direct_rule_domain = tls.domain

        if not all((self.__hostname, self.__port, self.__username, self.__password)):
            raise ValueError(f"{settings.__class__.__name__} not filled")

    @property
    def is_installed(self) -> bool:
        return deb_is_installed("mihomo")

    def _install(self):
        check_root()

        deb_store_path = DOWNLOAD_DIR / "mihomo.deb"

        logger.debug("Get mihomo package")
        download_file(self.__download_url, deb_store_path)

        logger.debug("Install package")
        install_deb(str(deb_store_path))

        config = render_config(
            hostname=self.__hostname,
            port=self.__port,
            username=self.__username,
            password=self.__password,
            quic=self.__use_quic,
            proxy_port=self.__proxy_port,
            direct_rule_domain=self.__direct_rule_domain
        )

        Path("/etc/mihomo/config.yaml").write_text(config)

    def _uninstall(self):
        check_root()

        logger.debug("Delete mihomo package")
        uninstall_deb("mihomo")

        logger.debug("Delete mihomo configuration")
        shutil.rmtree("/etc/mihomo")
