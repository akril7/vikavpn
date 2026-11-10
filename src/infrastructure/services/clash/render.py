from dataclasses import dataclass
from src.configuration.endpoints.mita import MitaProtocol
from src.domain.models import User
from src.infrastructure.templating import get_env

env = get_env(__file__)


@dataclass
class MitaConfig:
    protocol: MitaProtocol
    port: int | None = None
    port_range: str | None = None


@dataclass
class TrustTunnelConfig:
    port: int


def render_config(
        domain: str,
        user: User,
        mita_config: MitaConfig | None = None,
        trusttunnel_config: TrustTunnelConfig | None = None) -> str:
    template = env.get_template("config.yaml.j2")
    return template.render(
        domain=domain,
        user=user,
        mita=mita_config or False,
        trusttunnel=trusttunnel_config or False
    )
