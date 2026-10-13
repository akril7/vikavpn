from src.core.interfaces import Controller
from src.infrastructure.systemd import SystemdUnitController
from src.settings import HysteriaSettings


class HysteriaController(Controller):
    def __init__(self, hysteria: HysteriaSettings):
        self.__endpoint = SystemdUnitController(hysteria.service_name)
        self.__auth = SystemdUnitController(f"{hysteria.service_name}-auth")

    @property
    def status(self) -> bool:
        return self.__endpoint.status and self.__auth.status

    def start(self):
        self.__endpoint.start()
        self.__auth.start()

    def stop(self):
        self.__auth.stop()
        self.__endpoint.stop()

    def restart(self):
        self.__endpoint.restart()
        self.__auth.restart()

    def reload(self):
        self.__endpoint.reload()
