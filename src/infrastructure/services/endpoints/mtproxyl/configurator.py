from src.application.ports.services.callables import IsInstallCallback, ReloadControllerCallback
from src.application.services import BaseConfigurator
from src.configuration import MTProxyLSettings
from src.domain.models import Users
from src.infrastructure.system.subprocess import check_root
from src.domain.users.filters import filter_proxy_users

from .render import render_secrets


class MTProxyLConfigurator(BaseConfigurator):
    def __init__(self,
                 mtproxyl: MTProxyLSettings,
                 is_install_callback: IsInstallCallback,
                 reload_controller_callback: ReloadControllerCallback):
        super().__init__(is_install_callback, reload_controller_callback)
        self.__secrets_path = mtproxyl.secrets_path

    def _apply(self, users: Users):
        check_root()

        secrets = render_secrets(
            users=filter_proxy_users(users)
        )

        self.__secrets_path.parent.mkdir(parents=True, exist_ok=True)
        self.__secrets_path.write_text(secrets)
