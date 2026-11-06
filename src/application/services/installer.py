from abc import abstractmethod, ABC

from src.application.ports.services import InstallerError, Installer


class BaseInstaller(Installer, ABC):
    @abstractmethod
    def _install(self):
        """ Логика установки сервиса """
        pass

    @abstractmethod
    def _uninstall(self):
        """ Логика удаления сервиса"""
        pass

    def install(self):
        self._install()
        if not self.is_installed:
            raise InstallerError(f"Cannot install {type(self).__name__}")

    def uninstall(self):
        self._uninstall()
        if self.is_installed:
            raise InstallerError(f"Cannot uninstall {type(self).__name__}")
