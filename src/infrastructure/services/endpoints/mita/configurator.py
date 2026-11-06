from pathlib import Path

from src.domain.users.filters import filter_vpn_users
from src.application.ports.services.callables import IsInstallCallback, ReloadControllerCallback
from src.application.services.configurator import BaseConfigurator
from src.domain.models import Users
from src.infrastructure.system.subprocess import run_with_check
from src.configuration import MitaSettings

from .render import PortBindingsItem, render_config

CONFIG_PATH = Path("/tmp/mita.config.json")


class MitaConfigurator(BaseConfigurator):
    def __init__(self,
                 config: MitaSettings,
                 is_install_callback: IsInstallCallback,
                 reload_controller_callback: ReloadControllerCallback):
        super().__init__(is_install_callback=is_install_callback,
                         reload_controller_callback=reload_controller_callback)

        self.__portbinds = [PortBindingsItem(
            port_range=config.port_range,
            protocol=config.protocol
        )]

    def _apply(self, users: Users):
        config = render_config(
            port_bindings=self.__portbinds,
            users=filter_vpn_users(users)
        )

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(config)

        run_with_check(["mita", "apply", "config", str(CONFIG_PATH)])
        CONFIG_PATH.unlink(missing_ok=True)
