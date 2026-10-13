import shutil

from loguru import logger

from src.core.url_build.file import build_origin
from src.infrastructure.system.subprocess import check_root
from src.settings import HysteriaSettings, SiteSettings, TLSSettings
from src.infrastructure.systemd import SystemdUnitInstaller
from src.infrastructure.system import docker

from src.infrastructure.services.endpoints.hysteria.render import render_config, render_service


class HysteriaEndpointInstaller(SystemdUnitInstaller):
    def __init__(
            self,
            hysteria: HysteriaSettings,
            tls: TLSSettings,
            site: SiteSettings
    ):
        super().__init__(
            service_name=hysteria.service_name,
            service_file_content=render_service(
                container_name=hysteria.docker_container_name,
                image_name=hysteria.docker_image_name,
                config_path=str(hysteria.config_path),
                cert_path=str(tls.cert_path),
                key_path=str(tls.key_path),
            )
        )

        self.__container_name = hysteria.docker_container_name
        self.__image_name = hysteria.docker_image_name
        self.__install_dir = hysteria.install_dir
        self.__config_path = hysteria.config_path

        self.__tls = tls

        self.__config_content = render_config(
            port=hysteria.port,
            auth_url=hysteria.auth_url,
            mask_url=build_origin(tls.domain, site.port),
        )

    @property
    def is_installed(self) -> bool:
        return (
            docker.is_docker_install()
            and super().is_installed
        )

    def _install(self):
        check_root()

        if not docker.is_docker_install():
            logger.info("Install docker")
            docker.install_docker()

        logger.debug("Pull image")
        docker.pull_image(self.__image_name)

        logger.debug(f"Save config {self.__config_path}")
        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        self.__config_path.write_text(self.__config_content)

        super()._install()

    def _uninstall(self):
        check_root()

        logger.debug("Remove hysteria systemd unit")
        super()._uninstall()

        logger.debug("Remove hysteria container")
        docker.remove_container(self.__container_name)

        logger.debug("Remove hysteria image")
        docker.remove_image(self.__image_name)

        logger.debug("Remove hysteria dir")
        shutil.rmtree(self.__install_dir, ignore_errors=True)
