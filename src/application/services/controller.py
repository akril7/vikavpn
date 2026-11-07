from abc import ABC, abstractmethod

from src.application.ports.services import Controller
from src.application.ports.services.callables import IsInstallCallback


class BaseController(Controller, ABC):
    def __init__(self, is_install_callback: IsInstallCallback):
        self._is_install_callback = is_install_callback

    @property
    @abstractmethod
    def _status(self) -> bool:
        ...

    @abstractmethod
    def _reload(self):
        ...

    @property
    def status(self) -> bool:
        return self._is_install_callback() and self._status

    def reload(self):
        self.start()
        self._reload()
