import shutil

from loguru import logger

from src.application.services import BaseInstaller
from src.configuration import SiteSettings, NginxSettings, TLSSettings
from src.configuration.app import DOWNLOAD_DIR
from src.domain.urls.file import get_file_name

from src.infrastructure.utils.file import download_file, unpack_clean
from src.infrastructure.system.subprocess import deb_is_installed
from src.infrastructure.system.systemctl import SystemdUnit

from .render import render_nginx_config, Mount, render_stub


class SiteInstaller(BaseInstaller):
    def __init__(
            self,
            site: SiteSettings,
            nginx: NginxSettings,
            tls: TLSSettings,
            mounts: list[Mount] | None = None):
        self.__http_port = site.http_port
        self.__ssl_port = site.ssl_port
        self.__root = site.root_dir
        self.__stub_download_url = site.stub_download_url
        self.__guide_download_url = site.guide_download_url
        self.__guide_urlpath = site.guide_urlpath

        self.__service = SystemdUnit(nginx.service_name)
        self.__site_available = nginx.available_path / site.name
        self.__site_enabled = nginx.enabled_path / site.name
        self.__tls = tls

        self.__mounts = mounts or []

    @property
    def is_installed(self) -> bool:
        return self.__site_available.exists() and self.__site_enabled.exists()

    def _install(self):
        if not deb_is_installed("nginx"):
            logger.error("Cannot install site: Nginx not installed")
            return

        stub_html = render_stub(text="Unconfigured")
        nginx_config = render_nginx_config(
            http_port=self.__http_port,
            ssl_port=self.__ssl_port,
            root_dir=str(self.__root),
            mounts=self.__mounts,
            tls=self.__tls
        )

        self.__root.mkdir(parents=True, exist_ok=True)
        if self.__stub_download_url:
            logger.debug("Download stub")
            archive_path = DOWNLOAD_DIR / get_file_name(self.__stub_download_url)
            download_file(self.__stub_download_url, archive_path)
            unpack_clean(archive_path, self.__root)
        else:
            logger.debug("Save stub html")
            (self.__root / "index.html").write_text(stub_html)

        if self.__guide_download_url:
            relative_dirpath = str(self.__guide_urlpath.parent).removeprefix("/")
            dirpath = self.__root / relative_dirpath
            dirpath.mkdir(parents=True, exist_ok=True)

            logger.debug("Download guide")
            video_path = dirpath / self.__guide_urlpath.name
            download_file(self.__guide_download_url, video_path)

        logger.debug("Save site config")
        self.__site_available.parent.mkdir(parents=True, exist_ok=True)
        self.__site_available.write_text(nginx_config)

        logger.debug("Enable site")
        self.__site_enabled.parent.mkdir(parents=True, exist_ok=True)
        self.__site_enabled.unlink(missing_ok=True)
        self.__site_enabled.symlink_to(self.__site_available)

        logger.debug("Reload nginx")
        self.__service.reload()

    def _uninstall(self):
        logger.debug("Disable site")
        self.__site_enabled.unlink(missing_ok=True)

        logger.debug("Remove site config")
        self.__site_available.unlink(missing_ok=True)

        if self.__root.exists():
            logger.debug("Remove site root dir")
            shutil.rmtree(self.__root)

        logger.debug("Reload nginx")
        self.__service.reload()
