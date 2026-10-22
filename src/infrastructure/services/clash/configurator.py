from src.core.url_build.file import build_clash_ads_rules_url, build_origin
from src.settings import SiteSettings
from src.settings import ClashSettings
from src.settings import HysteriaSettings
from src.settings import MitaSettings
from src.settings import TLSSettings
from src.settings.endpoints.trusttunnel import TrustTunnelSettings
from src.db.models import Users
from src.core.interfaces.configurator import Configurator
from src.infrastructure.services.clash.render import MitaConfig, HysteriaConfig, TrustTunnelConfig, \
    render_config


class ClashConfigurator(Configurator):
    def __init__(self,
                 clash: ClashSettings,
                 tls: TLSSettings,
                 site: SiteSettings,
                 mita: MitaSettings,
                 hysteria: HysteriaSettings,
                 trusttunnel: TrustTunnelSettings):
        self.__config_dir = clash.configs_store_dir
        self.__domain = tls.domain
        self.__ads_rule_url = build_clash_ads_rules_url(build_origin(tls.domain, site.port))

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
                ads_rule_url=self.__ads_rule_url,
                mita_config=self.__mita_cfg,
                hysteria_config=self.__hysteria_cfg,
                trusttunnel_config=self.__trusttunnel_cfg
            )
            store_path = self.__config_dir / user.uuid.hex
            store_path.write_text(config)
