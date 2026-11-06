from src.application.ports.services.callables import IsInstallCallback
from src.application.services import BaseController
from src.infrastructure.systemd import SystemdUnitController
from src.configuration import HysteriaSettings


class HysteriaController(BaseController):
    def __init__(self, hysteria: HysteriaSettings, is_install_callback: IsInstallCallback):
        super().__init__(is_install_callback)
        self.__endpoint = SystemdUnitController(hysteria.service_name, is_install_callback)
        self.__auth = SystemdUnitController(f"{hysteria.service_name}-auth", is_install_callback)

    @property
    def _status(self) -> bool:
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

    def _reload(self):
        self.__endpoint.reload()
