from typing import Any

from src.application.ports.registry import InstallTargets, ControlTargets, ConfigureTargets
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

    def get_install_targets(self, names: list[str] | None = None) -> InstallTargets:
        return _filter(self.__installer_targets, names)

    def get_control_targets(self, names: list[str] | None = None) -> ControlTargets:
        return _filter(self.__controller_targets, names)

    def get_configure_targets(self, names: list[str] | None = None) -> ConfigureTargets:
        return _filter(self.__configurator_targets, names)


def _filter(storage, names: list[str] | None = None) -> dict[str, Any]:
    if not names:
        return dict(storage.items())

    for name in names:
        if name not in storage:
            raise ValueError(f"Цели с именем {name} не существует")

    return dict(filter(lambda v: v[0] in names, storage.items()))
