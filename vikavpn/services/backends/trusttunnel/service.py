from config.trusttunnel import TrustTunnelSettings
from services.backends.systemd import SystemdService


class TrustTunnelService(SystemdService):
    def __init__(self, config: TrustTunnelSettings):
        super().__init__(config.service)
