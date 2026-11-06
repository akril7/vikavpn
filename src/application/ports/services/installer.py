from abc import ABC, abstractmethod


class Installer(ABC):
    @property
    @abstractmethod
    def is_installed(self) -> bool:
        """ Установлен ли сервис? """
        pass

    @abstractmethod
    def install(self):
        """ Установить сервис """
        pass

    @abstractmethod
    def uninstall(self):
        """ Удалить сервис """
        pass
