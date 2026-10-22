from src.infrastructure.app import AppInstaller
from src.settings import HysteriaSettings


class HysteriaAuthInstaller(AppInstaller):
    def __init__(self, hysteria: HysteriaSettings):
        super().__init__(
            appname="hysteria_auth",
            desc="Hysteria Auth Service",
            requires=[hysteria.service_name]
        )
