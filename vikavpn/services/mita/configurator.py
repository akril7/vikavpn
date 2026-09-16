from config.mita import MitaSettings
from database.models import Users
from services.base import Configurator, ConfiguratorError
from services.mita.exceptions import MitaApplyConfigError
from services.mita.render import PortBindingsItem, render_config
from utils.subprocess import run_and_get_text
from utils.systemctl import SystemdService


class MitaConfigurator(Configurator):
    def __init__(self, config: MitaSettings):
        self.__config_path = config.config_path
        self.__service = SystemdService(config.service)
        self.__portbinds = [PortBindingsItem(
            port_range=config.port_range,
            protocol=config.protocol
        )]

    def apply(self, users: Users):
        config = render_config(
            port_bindings=self.__portbinds,
            users=users
        )

        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        self.__config_path.write_text(config)

        output = run_and_get_text(["mita", "apply", "config", self.__config_path])
        if len(output) > 0:
            raise MitaApplyConfigError(output)

        self.__start_mita_service()

    def __start_mita_service(self):
        if self.__service.status:
            return

        self.__service.start()

        if not self.__service.status:
            raise ConfiguratorError("Mita service not started")
