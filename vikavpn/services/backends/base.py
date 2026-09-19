from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from database.models import Users


class InstallerError(Exception):
    pass


class ServiceError(Exception):
    pass


class ConfiguratorError(Exception):
    pass


class Installer(ABC):
    @property
    @abstractmethod
    def is_installed(self) -> bool:
        pass

    def install(self, force: bool = False):
        self._install(force=force)
        self.check_installation()

    def uninstall(self):
        self._uninstall()
        self.check_uninstallation()

    @abstractmethod
    def _install(self, force: bool = False):
        pass

    @abstractmethod
    def _uninstall(self):
        pass

    def check_installation(self):
        if not self.is_installed:
            raise InstallerError(f"{type(self).__name__} not installed")

    def check_uninstallation(self):
        if self.is_installed:
            raise InstallerError(f"{type(self).__name__} not uninstalled")


class StubInstaller(Installer):
    def __init__(self, name: str = "stub", installed: bool = False):
        self.name = name
        self._installed = installed
        self.install_calls: list[bool] = []
        self.uninstall_calls: int = 0

    @property
    def is_installed(self) -> bool:
        return self._installed

    def _install(self, force: bool = False) -> None:
        self.install_calls.append(force)
        self._installed = True

    def _uninstall(self) -> None:
        self.uninstall_calls += 1
        self._installed = False


class Service(ABC):
    @property
    @abstractmethod
    def status(self) -> bool:
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def restart(self):
        pass


class StubService(Service):
    @property
    def status(self) -> bool:
        return True

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass


class Configurator(ABC):
    @abstractmethod
    def apply(self, users: Users):
        pass


class StubConfigurator(Configurator):
    def apply(self, users: Users):
        pass


def get_env(base_file: str) -> Environment:
    """base_file — обычно __file__ вызывающего модуля."""
    templates_dir = Path(base_file).resolve().parent / "templates"
    return Environment(loader=FileSystemLoader(templates_dir))
