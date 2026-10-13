import shutil

from loguru import logger

from src.core.interfaces import Installer
from src.settings import Settings
from src.settings.app import FILES_DIR

from src.infrastructure.system.subprocess import deb_is_installed
from src.infrastructure.system.systemctl import SystemdUnit

from .render import render_index_html, render_nginx_config, Mount


class SiteInstaller(Installer):
    def __init__(self, settings: Settings):
        self.__title = settings.site.title
        self.__port = settings.site.port
        self.__extra_ports = settings.site.extra_ports
        self.__root = settings.site.root_dir

        self.__service = SystemdUnit(settings.nginx.service_name)
        self.__site_available = settings.nginx.available_path / settings.site.name
        self.__site_enabled = settings.nginx.enabled_path / settings.site.name
        self.__tls = settings.tls

        self.__mounts = [
            Mount("/files/", str(FILES_DIR)),
            Mount(settings.clash.configs_urlpath, str(settings.clash.configs_store_dir)),
            Mount(
                location=settings.payments.payment_path,
                destination=settings.payments.origin,
                is_proxy=True,
            )
        ]

    @property
    def is_installed(self) -> bool:
        return self.__site_available.exists() and self.__site_enabled.exists()

    def _install(self):
        if not deb_is_installed("nginx"):
            logger.error("Cannot install site: Nginx not installed")
            return

        index_html = render_index_html(title=self.__title)
        nginx_config = render_nginx_config(
            port=self.__port,
            extra_ports=self.__extra_ports,
            root_dir=str(self.__root),
            mounts=self.__mounts,
            tls=self.__tls
        )

        logger.info("Save index.html")
        self.__root.mkdir(parents=True, exist_ok=True)
        (self.__root / "index.html").write_text(index_html)

        logger.info("Save site config")
        self.__site_available.parent.mkdir(parents=True, exist_ok=True)
        self.__site_available.write_text(nginx_config)

        logger.info("Enable site")
        self.__site_enabled.parent.mkdir(parents=True, exist_ok=True)
        self.__site_enabled.unlink(missing_ok=True)
        self.__site_enabled.symlink_to(self.__site_available)

        logger.info("Reload nginx")
        self.__service.reload()

    def _uninstall(self):
        logger.info("Disable site")
        self.__site_enabled.unlink(missing_ok=True)

        logger.info("Remove site config")
        self.__site_available.unlink(missing_ok=True)

        if self.__root.exists():
            logger.info("Remove site root dir")
            shutil.rmtree(self.__root)

        logger.info("Reload nginx")
        self.__service.reload()
