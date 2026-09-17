import shutil

from loguru import logger

from config.ssl import TLSSettings
from config.webserver import WebServerSettings
from services.base import Installer
from services.webserver.render import render_index_html, render_nginx_config
from utils import SSLPaths
from utils.subprocess import is_installed, install
from utils.systemctl import SystemdService


class WebServerInstaller(Installer):
    def __init__(self, ws_config: WebServerSettings, tls_config: TLSSettings):
        self.__ports = ws_config.ports
        self.__root = ws_config.root
        self.__title = ws_config.title
        self.__nginx_available_path = ws_config.nginx_site_available
        self.__nginx_enabled_path = ws_config.nginx_site_enabled
        self.__service = SystemdService(ws_config.nginx.service_name)
        self.__mounts = ws_config.mounts
        self.__domain = tls_config.domain
        self.__ssl_paths = SSLPaths(cert=str(tls_config.cert_path), key=str(tls_config.key_path))

    @property
    def is_installed(self) -> bool:
        return self.__nginx_available_path.exists() and self.__nginx_enabled_path.exists()

    def _install(self, force: bool = False):
        if self.is_installed and not force:
            logger.info("Webserver already installed")
            return

        index_html = render_index_html(title=self.__title)
        nginx_config = render_nginx_config(
            ports=self.__ports,
            server_name=self.__domain,
            web_root=str(self.__root),
            mounts=self.__mounts,
            ssl_paths=self.__ssl_paths
        )

        if not is_installed("nginx"):
            logger.info("Install nginx")
            install("nginx")

        logger.info("Save index.html")
        self.__root.mkdir(parents=True, exist_ok=True)
        (self.__root / "index.html").write_text(index_html)

        logger.info("Save webserver config")
        self.__nginx_available_path.parent.mkdir(parents=True, exist_ok=True)
        self.__nginx_available_path.write_text(nginx_config)

        logger.info("Enable webserver config")
        self.__nginx_enabled_path.parent.mkdir(parents=True, exist_ok=True)
        self.__nginx_enabled_path.unlink(missing_ok=True)
        self.__nginx_enabled_path.symlink_to(self.__nginx_available_path)

        logger.info("Reload nginx")
        self.__service.reload()

    def _uninstall(self):
        logger.info("Disable webserver config")
        self.__nginx_enabled_path.unlink(missing_ok=True)

        logger.info("Remove webserver config")
        self.__nginx_available_path.unlink(missing_ok=True)

        if self.__root.exists():
            logger.info("Remove webserver root dir")
            shutil.rmtree(self.__root)

        logger.info("Reload nginx service")
        self.__service.reload()
