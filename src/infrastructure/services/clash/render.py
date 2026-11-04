from dataclasses import dataclass
from src.settings.endpoints.mita import MitaProtocol
from src.db.models import User
from src.infrastructure import get_env

env = get_env(__file__)


@dataclass
class MitaConfig:
    protocol: MitaProtocol
    port: int | None = None
    port_range: str | None = None


@dataclass
class HysteriaConfig:
    port: int


@dataclass
class TrustTunnelConfig:
    port: int


def render_config(
        domain: str,
        user: User,
        mita_config: MitaConfig | None = None,
        hysteria_config: HysteriaConfig | None = None,
        trusttunnel_config: TrustTunnelConfig | None = None) -> str:
    template = env.get_template("config.yaml.j2")
    return template.render(
        domain=domain,
        user=user,
        mita=mita_config or False,
        hysteria=hysteria_config or False,
        trusttunnel=trusttunnel_config or False
    )
