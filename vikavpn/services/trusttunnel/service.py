from config.trusttunnel import TrustTunnelSettings
from services.base import Service
from utils.systemctl import SystemdService


class TrustTunnelService(Service):
    def __init__(self, config: TrustTunnelSettings):
        self.__service = SystemdService(config.service)

    @property
    def status(self) -> bool:
        return self.__service.status()

    def start(self):
        self.__service.enable()
        self.__service.start()

    def stop(self):
        self.__service.stop()

    def restart(self):
        self.__service.restart()
