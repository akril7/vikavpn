from src.settings import TLSSettings, TrustTunnelSettings
from src.db.models import Users
from src.core.interfaces.configurator import Configurator
from src.infrastructure.system.systemctl import SystemdUnit
from src.users.filters import filter_vpn_users

from .render import render_hosts, render_settings, render_users


class TrustTunnelConfigurator(Configurator):
    def __init__(self, trusttunnel: TrustTunnelSettings, tls: TLSSettings):
        self.__service = SystemdUnit(trusttunnel.service_name)
        self.__install_dir = trusttunnel.install_dir

        self.__hosts_content = render_hosts(tls=tls, allowed_sni=[trusttunnel.sni])
        self.__vpn_content = render_settings(port=trusttunnel.port)

    def apply(self, users: Users):
        users_config = render_users(
            users=filter_vpn_users(users)
        )

        (self.__install_dir / "hosts.toml").write_text(self.__hosts_content)
        (self.__install_dir / "vpn.toml").write_text(self.__vpn_content)
        (self.__install_dir / "credentials.toml").write_text(users_config)

        self.__service.reload()
