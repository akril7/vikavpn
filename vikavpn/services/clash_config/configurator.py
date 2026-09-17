from config.clash import ClashSettings
from config.hysteria import HysteriaSettings
from config.mita import MitaSettings
from config.ssl import TLSSettings
from config.trusttunnel import TrustTunnelSettings
from database.models import Users
from services.base import Configurator
from services.clash_config.render import render_many_configs, MitaConfig, HysteriaConfig, TrustTunnelConfig


class ClashConfigurator(Configurator):
    def __init__(self, clash_config: ClashSettings, tls_config: TLSSettings,
                 mita_config: MitaSettings, hysteria_config: HysteriaSettings, trusttunnel_config: TrustTunnelSettings):
        self.__config_dir = clash_config.configs_store_dir
        self.__domain = tls_config.domain
        self.__rules_base_url = f"https://{tls_config.domain}/files/rules"
        self.__mita_cfg = MitaConfig(protocol=mita_config.protocol, port_range=mita_config.port_range)
        self.__hysteria_cfg = HysteriaConfig(port=hysteria_config.port)
        self.__trusttunnel_cfg = TrustTunnelConfig(port=trusttunnel_config.port)

    def apply(self, users: Users):
        self.__config_dir.mkdir(parents=True, exist_ok=True)

        for uuid, config in render_many_configs(
                domain=self.__domain,
                users=users,
                rules_base_url=self.__rules_base_url,
                mita_config=self.__mita_cfg,
                hysteria_config=self.__hysteria_cfg,
                trusttunnel_config=self.__trusttunnel_cfg):
            (self.__config_dir / uuid.hex).write_text(config)
