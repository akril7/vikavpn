from abc import ABC, abstractmethod

from .errors import InstallerError


class Installer(ABC):
    @property
    @abstractmethod
    def is_installed(self) -> bool:
        """ Установлен ли сервис? """
        pass

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
        """ Удалить сервис """
        self._uninstall()
        if self.is_installed:
            raise InstallerError(f"Cannot uninstall {type(self).__name__}")
