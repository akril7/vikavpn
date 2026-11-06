from abc import ABC, abstractmethod

from src.application.ports.services import Configurator, ConfiguratorError
from src.application.ports.services.callables import IsInstallCallback, ReloadControllerCallback
from src.domain.models import Users


class BaseConfigurator(Configurator, ABC):
    def __init__(
            self,
            is_install_callback: IsInstallCallback,
            reload_controller_callback: ReloadControllerCallback
    ):
        self._is_install_callback = is_install_callback
        self._reload_controller_callback = reload_controller_callback

    @abstractmethod
    def _apply(self, users: Users):
        """ Применить список пользователей для ендпоинта """
        pass

    def apply(self, users: Users):
        if not self._is_install_callback():
            raise ConfiguratorError("Target not installed")

        self._apply(users=users)
        self._reload_controller_callback()
