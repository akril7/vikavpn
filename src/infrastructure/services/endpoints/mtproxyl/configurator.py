from src.core.interfaces import Controller
from src.settings import MTProxyLSettings
from src.db.models import Users
from src.core.interfaces.configurator import Configurator
from src.infrastructure.system.subprocess import check_root
from src.core.users.filters import filter_proxy_users

from .render import render_secrets


class MTProxyLConfigurator(Configurator):
    def __init__(self, mtproxyl: MTProxyLSettings, controller: Controller):
        self.__controller = controller
        self.__secrets_path = mtproxyl.secrets_path

    def apply(self, users: Users):
        check_root()

        secrets = render_secrets(
            users=filter_proxy_users(users)
        )

        self.__secrets_path.parent.mkdir(parents=True, exist_ok=True)
        self.__secrets_path.write_text(secrets)

        self.__controller.reload()
