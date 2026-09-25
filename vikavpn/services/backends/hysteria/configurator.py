from settings.hysteria import HysteriaSettings
from database.models import Users
from services.backends.base import Configurator
from services.backends.hysteria import HysteriaService
from services.backends.hysteria.render import render_config


class HysteriaConfigurator(Configurator):
    def __init__(self, config: HysteriaSettings):
        self.__port = config.port
        self.__mask_url = config.mask_url
        self.__config_path = config.config_path

        self.__service = HysteriaService(config)

    def apply(self, users: Users):
        config = render_config(
            port=self.__port,
            mask_url=self.__mask_url,
            users=users
        )

        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        self.__config_path.write_text(config)

        self.__service.restart()
