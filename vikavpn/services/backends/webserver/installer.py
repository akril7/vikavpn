import shutil

from loguru import logger

from settings.tls import TLSSettings
from settings.webserver import WebServerSettings
from services.backends.base import Installer
from services.system.subprocess import is_installed
from services.system.systemctl import SystemdDaemon

from .render import render_index_html, render_nginx_config


class WebServerInstaller(Installer):
    def __init__(self, ws_config: WebServerSettings, tls_config: TLSSettings):
        self.__port = ws_config.port
        self.__root = ws_config.root
        self.__title = ws_config.title
        self.__site_available = ws_config.site_available
        self.__site_enabled = ws_config.site_enabled
        self.__service = SystemdDaemon(ws_config.nginx.service_name)
        self.__mounts = ws_config.mounts
        self.__proxy_passes = ws_config.proxy_passes
        self.__tls = tls_config

    @property
    def is_installed(self) -> bool:
        return self.__site_available.exists() and self.__site_enabled.exists()

    def _install(self, force: bool = False):
        if self.is_installed and not force:
            logger.info("Webserver already installed")
            return

        index_html = render_index_html(title=self.__title)
        nginx_config = render_nginx_config(
            port=self.__port,
            web_root=str(self.__root),
            mounts=self.__mounts,
            proxy_passes=self.__proxy_passes,
            tls=self.__tls
        )

        if not is_installed("nginx"):
            logger.error("Nginx not installed")
            return

        logger.info("Save index.html")
        self.__root.mkdir(parents=True, exist_ok=True)
        (self.__root / "index.html").write_text(index_html)

        logger.info("Save webserver config")
        self.__site_available.parent.mkdir(parents=True, exist_ok=True)
        self.__site_available.write_text(nginx_config)

        logger.info("Enable webserver config")
        self.__site_enabled.parent.mkdir(parents=True, exist_ok=True)
        self.__site_enabled.unlink(missing_ok=True)
        self.__site_enabled.symlink_to(self.__site_available)

        logger.info("Reload nginx")
        self.__service.reload()

    def _uninstall(self):
        logger.info("Disable webserver config")
        self.__site_enabled.unlink(missing_ok=True)

        logger.info("Remove webserver config")
        self.__site_available.unlink(missing_ok=True)

        if self.__root.exists():
            logger.info("Remove webserver root dir")
            shutil.rmtree(self.__root)

        logger.info("Reload nginx service")
        self.__service.reload()
