from typing import Protocol

from src.application.ports.services import Configurator, Controller, Installer

InstallTargets = dict[str, Installer]
ConfigureTargets = dict[str, Configurator]
ControlTargets = dict[str, Controller]


class RegistryLike(Protocol):
    def get_install_targets(self, names: list[str] | None = None) -> InstallTargets:
        ...

    def get_control_targets(self, names: list[str] | None = None) -> ControlTargets:
        ...

    def get_configure_targets(self, names: list[str] | None = None) -> ConfigureTargets:
        ...
