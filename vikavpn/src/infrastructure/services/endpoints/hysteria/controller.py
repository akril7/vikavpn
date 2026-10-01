from src.settings import HysteriaSettings
from src.core.interfaces.controller import Controller
from src.infrastructure.system.docker import is_container_running, restart_container, start_container, stop_container


class HysteriaController(Controller):
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

    def reload(self):
        pass
