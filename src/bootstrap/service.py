from loguru import logger

from src.application.ports.services import Installer, Controller, Configurator
from src.domain.models import Users


def dummy_invoke_msg(name: str):
    def wrapper(*_, **__) -> bool:
        logger.warning(f"DUMMY INVOKE {name}")
        return False
    return wrapper


class Service(Installer, Controller, Configurator):
    def __init__(
            self,
            installer: Installer | None = None,
            controller: Controller | None = None,
            configurator: Configurator | None = None,
            logname: str = ""
    ):
        self.__installer = installer
        self.__controller = controller
        self.__configurator = configurator
        self.__dummy = dummy_invoke_msg(name=logname)

    @property
    def installer(self) -> Installer | None:
        return self.__installer

    @property
    def controller(self) -> Controller | None:
        return self.__controller

    @property
    def configurator(self) -> Configurator | None:
        return self.__configurator

    @property
    def is_installed(self) -> bool:
        v = getattr(self.installer, "is_installed", None)
        return v if v is not None else self.__dummy()

    def install(self):
        getattr(self.installer, "install", self.__dummy)()

    def uninstall(self):
        getattr(self.installer, "uninstall", self.__dummy)()

    @property
    def status(self) -> bool:
        v = getattr(self.controller, "status", None)
        return v if v is not None else self.__dummy()

    def start(self):
        getattr(self.controller, "start", self.__dummy)()

    def stop(self):
        getattr(self.controller, "stop", self.__dummy)()

    def restart(self):
        getattr(self.controller, "restart", self.__dummy)()

    def reload(self):
        getattr(self.controller, "reload", self.__dummy)()

    def apply(self, users: Users):
        getattr(self.configurator, "apply", self.__dummy)(users)
