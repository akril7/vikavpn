from src.settings import MTProxyLSettings
from src.db.models import Users
from src.core.interfaces.configurator import Configurator
from src.infrastructure.system.subprocess import run_with_check, check_root

from .render import render_secrets


class MTProxyLConfigurator(Configurator):
    def __init__(self, mtproxyl: MTProxyLSettings):
        self.__default_user = mtproxyl.default_user
        self.__default_user_uuid = mtproxyl.default_user_uuid
        self.__secrets_path = mtproxyl.secrets_path

    def apply(self, users: Users):
        check_root()

        secrets = render_secrets(
            default_user=self.__default_user,
            default_user_uuid=self.__default_user_uuid,
            users=users
        )

        self.__secrets_path.parent.mkdir(parents=True, exist_ok=True)
        self.__secrets_path.write_text(secrets)

        # Update telemt config
        run_with_check(["mtproxyl", "secret", "enable", self.__default_user])
