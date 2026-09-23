from loguru import logger

from config.app import SNI
from config.tls import TLSSettings
from config.trusttunnel import TrustTunnelSettings
from database.models import Users
from services.backends.base import Configurator, ConfiguratorError
from services.backends.trusttunnel.render import render_hosts, render_settings, render_users_config
from services.system.systemctl import SystemdDaemon


class TrustTunnelConfigurator(Configurator):
    def __init__(self, trusttunnel_config: TrustTunnelSettings, tls_config: TLSSettings):
        self.__service = SystemdDaemon(trusttunnel_config.service)
        self.__install_dir = trusttunnel_config.install_dir
        self.__port = trusttunnel_config.port
        self.__domain = tls_config.domain
        self.__tls = tls_config
        self.__allowed_sni = [SNI]

    def apply(self, users: Users):
        hosts = render_hosts(
            hostname=self.__domain,
            tls=self.__tls,
            allowed_sni=self.__allowed_sni
        )

        settings = render_settings(port=self.__port)

        users_config = render_users_config(users=users)

        (self.__install_dir / "hosts.toml").write_text(hosts)
        (self.__install_dir / "vpn.toml").write_text(settings)
        (self.__install_dir / "credentials.toml").write_text(users_config)

        if not users:
            logger.error("Trusttunnel cannot start with zero users configuration")
            return

        self.__service.enable()
        self.__service.restart()

        if not self.__service.status():
            raise ConfiguratorError("Trusttunnel service not started")
