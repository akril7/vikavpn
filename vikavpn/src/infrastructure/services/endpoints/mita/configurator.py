from pathlib import Path

from src.db.models import Users
from src.core.interfaces.configurator import Configurator
from src.core.interfaces import ConfiguratorError
from src.infrastructure.system.systemctl import SystemdUnit
from src.infrastructure.system.subprocess import run_and_get_text
from src.settings import MitaSettings
from src.users.filters import filter_vpn_users

from .render import PortBindingsItem, render_config

CONFIG_PATH = Path("/tmp/mita.config.json")


class MitaConfigurator(Configurator):
    def __init__(self, config: MitaSettings):
        self.__service = SystemdUnit(config.service_name)
        self.__portbinds = [PortBindingsItem(
            port_range=config.port_range,
            protocol=config.protocol
        )]

    def apply(self, users: Users):
        config = render_config(
            port_bindings=self.__portbinds,
            users=filter_vpn_users(users)
        )

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(config)

        output = run_and_get_text(["mita", "apply", "config", str(CONFIG_PATH)])
        if len(output) > 0:
            raise ConfiguratorError(output)

        self.__start_mita_service()

        CONFIG_PATH.unlink(missing_ok=True)

    def __start_mita_service(self):
        if self.__service.status:
            return

        self.__service.start()

        if not self.__service.status:
            raise ConfiguratorError("Mita service not started")
