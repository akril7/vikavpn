from src.configuration import ClashSettings
from src.configuration import HysteriaSettings
from src.configuration import MitaSettings
from src.configuration import TLSSettings
from src.configuration.endpoints.trusttunnel import TrustTunnelSettings
from src.domain.models import Users
from src.application.ports.services import Configurator
from src.infrastructure.services.clash.render import MitaConfig, HysteriaConfig, TrustTunnelConfig, \
    render_config


class ClashConfigurator(Configurator):
    def __init__(self,
                 clash: ClashSettings,
                 tls: TLSSettings,
                 mita: MitaSettings,
                 hysteria: HysteriaSettings,
                 trusttunnel: TrustTunnelSettings):
        self.__config_dir = clash.configs_store_dir
        self.__domain = tls.domain

        self.__hysteria_cfg = HysteriaConfig(port=hysteria.port)
        self.__trusttunnel_cfg = TrustTunnelConfig(port=trusttunnel.port)
        self.__mita_cfg = MitaConfig(protocol=mita.protocol,
                                     port_range=mita.port_range)

    def apply(self, users: Users):
        self.__config_dir.mkdir(parents=True, exist_ok=True)

        for user in users:
            config = render_config(
                user=user,
                domain=self.__domain,
                mita_config=self.__mita_cfg,
                hysteria_config=self.__hysteria_cfg,
                trusttunnel_config=self.__trusttunnel_cfg
            )
            store_path = self.__config_dir / user.uuid.hex
            store_path.write_text(config)
