from config.hysteria import HysteriaSettings
from database.models import Users
from services.base import Configurator
from services.hysteria import HysteriaService
from services.hysteria.render import render_config


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
