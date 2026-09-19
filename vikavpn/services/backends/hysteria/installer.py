from loguru import logger

from config.hysteria import HysteriaSettings
from config.tls import TLSSettings
from services.backends.base import Installer, InstallerError
from services.system import docker


class HysteriaInstaller(Installer):
    def __init__(self, hysteria_config: HysteriaSettings, tls_config: TLSSettings):
        self.__container_name = hysteria_config.docker_container_name
        self.__image_name = hysteria_config.docker_image_name
        self.__config_path = hysteria_config.config_path
        self.__tls = tls_config

    @property
    def is_installed(self) -> bool:
        return docker.is_docker_install() and docker.is_container_exists(self.__container_name)

    def _install(self, force: bool = False):
        if self.is_installed:
            logger.info("Hysteria already installed")

        if not docker.is_docker_install():
            logger.info("Install docker")
            docker.install_docker()

        if docker.is_container_exists(self.__container_name):
            if force:
                docker.stop_container(self.__container_name)
                docker.remove_container(self.__container_name)
            else:
                raise InstallerError(f"Container '{self.__container_name}' already exists. Use force install")

        logger.info("Pull hysteria docker image")
        docker.pull_image(self.__image_name)

        logger.info("Create hysteria docker container")
        docker.create_container(self.__container_name, self.__image_name,
                                ["--network", "host",
                                 "-v", f"{self.__tls.cert_path}:/app/server.crt",
                                 "-v", f"{self.__tls.key_path}:/app/server.key",
                                 "-v", f"{self.__config_path}:/etc/hysteria/server.yaml"]
                                )

    def _uninstall(self):
        if not docker.is_container_exists(self.__container_name):
            logger.info("Hysteria installation not found")
            return

        docker.check_docker_install()

        logger.info("Remove hysteria container")
        docker.remove_container(self.__container_name)

        logger.info("Remove hysteria image")
        docker.remove_image(self.__image_name)
