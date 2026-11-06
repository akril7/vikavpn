from src.application.ports.services.callables import IsInstallCallback, ReloadControllerCallback
from src.application.services import BaseConfigurator
from src.configuration import TLSSettings, TrustTunnelSettings
from src.configuration.app import PROXY_SOCKS5_ADDRESS
from src.domain.models import Users
from src.domain.users.filters import filter_vpn_users

from .render import render_hosts, render_settings, render_users


class TrustTunnelConfigurator(BaseConfigurator):
    def __init__(self,
                 trusttunnel: TrustTunnelSettings,
                 tls: TLSSettings,
                 is_install_callback: IsInstallCallback,
                 reload_controller_callback: ReloadControllerCallback):
        super().__init__(is_install_callback, reload_controller_callback)

        self.__install_dir = trusttunnel.install_dir
        self.__default_user = trusttunnel.default_user

        self.__hosts_content = render_hosts(tls=tls, allowed_sni=[trusttunnel.sni])
        self.__vpn_content = render_settings(port=trusttunnel.port, socks5_address=PROXY_SOCKS5_ADDRESS)

    def _apply(self, users: Users):
        users_config = render_users(
            users=filter_vpn_users(users),
            default_user=self.__default_user
        )

        (self.__install_dir / "hosts.toml").write_text(self.__hosts_content)
        (self.__install_dir / "vpn.toml").write_text(self.__vpn_content)
        (self.__install_dir / "credentials.toml").write_text(users_config)
