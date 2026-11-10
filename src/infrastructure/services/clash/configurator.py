from src.application.ports.services.callables import IsInstallCallback
from src.configuration import ClashSettings
from src.configuration import MitaSettings
from src.configuration import TLSSettings
from src.configuration.endpoints.trusttunnel import TrustTunnelSettings
from src.domain.models import Users
from src.application.ports.services import Configurator
from src.infrastructure.services.clash.render import MitaConfig, TrustTunnelConfig, \
    render_config


class ClashConfigurator(Configurator):
    def __init__(self,
                 clash: ClashSettings,
                 tls: TLSSettings,
                 mita: MitaSettings,
                 mita_is_install_callback: IsInstallCallback,
                 trusttunnel: TrustTunnelSettings,
                 trusttunnel_is_install_callback: IsInstallCallback):
        self.__config_dir = clash.configs_store_dir
        self.__domain = tls.domain

        self.__trusttunnel_cfg = TrustTunnelConfig(port=trusttunnel.port)
        self.__mita_cfg = MitaConfig(protocol=mita.protocol,
                                     port_range=mita.port_range)

        self.__mita_is_install_callback = mita_is_install_callback
        self.__trusttunnel_is_install_callback = trusttunnel_is_install_callback

    def apply(self, users: Users):
        self.__config_dir.mkdir(parents=True, exist_ok=True)

        for user in users:
            config = render_config(
                user=user,
                domain=self.__domain,
                mita_config=self.__mita_cfg if self.__mita_is_install_callback() else None,
                trusttunnel_config=self.__trusttunnel_cfg if self.__trusttunnel_is_install_callback else None
            )
            store_path = self.__config_dir / user.uuid.hex
            store_path.write_text(config)
