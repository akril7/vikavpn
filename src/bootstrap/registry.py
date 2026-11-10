from src.application.ports.services import Installer, Controller, Configurator
from src.bootstrap.builder import build_services
from src.configuration import Settings


class Registry:
    def __init__(self, settings: Settings):
        self.__settings = settings

        (self.__installer_targets,
         self.__controller_targets,
         self.__configurator_targets) = build_services(settings)

    @property
    def settings(self) -> Settings:
        return self.__settings

    def get_names_of_installers(self) -> list[str]:
        return list(self.__installer_targets.keys())

    def get_names_of_controllers(self) -> list[str]:
        return list(self.__controller_targets.keys())

    def get_names_of_configurator(self) -> list[str]:
        return list(self.__configurator_targets.keys())

    def get_installer(self, name: str) -> Installer:
        return self.__installer_targets[name]

    def get_controller(self, name: str) -> Controller:
        return self.__controller_targets[name]

    def get_configurator(self, name: str) -> Configurator:
        return self.__configurator_targets[name]
