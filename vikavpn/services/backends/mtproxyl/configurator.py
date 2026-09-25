from settings.mtproxyl import MTProxyLSettings
from database.models import Users
from services.backends.base import Configurator
from services.backends.mtproxyl.render import render_secrets
from services.system.subprocess import run_with_check, check_root


class MTProxyLConfigurator(Configurator):
    def __init__(self, mtproxyl_config: MTProxyLSettings):
        self.__default_user = mtproxyl_config.default_user
        self.__default_user_uuid = mtproxyl_config.default_user_uuid
        self.__secrets_path = mtproxyl_config.secrets_path

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
