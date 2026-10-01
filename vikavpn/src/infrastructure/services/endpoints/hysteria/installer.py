import shutil

from loguru import logger

from src.core.url_build.file import build_origin
from src.settings import HysteriaSettings, SiteSettings, WebhookSettings, TLSSettings
from src.core.interfaces import Installer
from src.infrastructure.system import docker

from .render import render_config


class HysteriaInstaller(Installer):
    def __init__(self, hysteria: HysteriaSettings, tls: TLSSettings, site: SiteSettings, webhook: WebhookSettings):
        self.__container_name = hysteria.docker_container_name
        self.__image_name = hysteria.docker_image_name
        self.__install_dir = hysteria.install_dir
        self.__config_path = hysteria.config_path

        self.__tls = tls

        self.__config_content = render_config(
            port=hysteria.port,
            auth_url=webhook.hysteria_url,
            mask_url=build_origin(tls.domain, site.port),
        )

    @property
    def is_installed(self) -> bool:
        return docker.is_docker_install() and docker.is_container_exists(self.__container_name)

    def _install(self):
        if not docker.is_docker_install():
            logger.info("Install docker")
            docker.install_docker()

        logger.info("Pull image")
        docker.pull_image(self.__image_name)

        logger.info(f"Save config {self.__config_path}")
        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        self.__config_path.write_text(self.__config_content)

        logger.info("Create container")
        docker.create_container(self.__container_name, self.__image_name,
                                ["--network", "host",
                                 "-v", f"{self.__tls.cert_path}:/app/server.crt",
                                 "-v", f"{self.__tls.key_path}:/app/server.key",
                                 "-v", f"{self.__config_path}:/etc/hysteria/server.yaml"]
                                )

    def _uninstall(self):
        logger.info("Remove hysteria container")
        docker.remove_container(self.__container_name)

        logger.info("Remove hysteria image")
        docker.remove_image(self.__image_name)

        logger.info("Remove hysteria dir")
        shutil.rmtree(self.__install_dir)
