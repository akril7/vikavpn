from src.application.ports.services import Installer, Controller, Configurator
from src.bootstrap.builder import build_services
from src.bootstrap.service import Service
from src.configuration import Settings


class Registry:
    def __init__(self, settings: Settings):
        self.__settings = settings

        self.__services = build_services(settings)
        self.__installers_names = _filter(self.__services, "installer")
        self.__controllers_names = _filter(self.__services, "controller")
        self.__configurators_names = _filter(self.__services, "configurator")

    @property
    def settings(self) -> Settings:
        return self.__settings

    @property
    def names_of_installers(self) -> list[str]:
        return self.__installers_names

    @property
    def names_of_controllers(self) -> list[str]:
        return self.__controllers_names

    @property
    def names_of_configurators(self) -> list[str]:
        return self.__configurators_names

    def get_installer(self, name: str) -> Installer:
        if name not in self.names_of_installers:
            raise KeyError(f"Cannot get installer: {name}")
        return self.__services[name]

    def get_controller(self, name: str) -> Controller:
        if name not in self.names_of_controllers:
            raise KeyError(f"Cannot get controller: {name}")
        return self.__services[name]

    def get_configurator(self, name: str) -> Configurator:
        if name not in self.names_of_configurators:
            raise KeyError(f"Cannot get configurator: {name}")
        return self.__services[name]


def _filter(services: dict[str, Service], attr: str) -> list[str]:
    return list(
        map(lambda x: x[0],
            filter(lambda x: getattr(x[1], attr) is not None, services.items()))
    )
