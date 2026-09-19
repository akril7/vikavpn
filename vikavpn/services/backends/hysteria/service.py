from config.hysteria import HysteriaSettings
from services.backends.base import Service
from services.system.docker import is_container_running, restart_container, start_container, stop_container


class HysteriaService(Service):
    def __init__(self, config: HysteriaSettings):
        self.__container_name = config.docker_container_name

    @property
    def status(self) -> bool:
        return is_container_running(self.__container_name)

    def start(self):
        start_container(self.__container_name)

    def stop(self):
        stop_container(self.__container_name)

    def restart(self):
        restart_container(self.__container_name)
