import uuid
from dataclasses import dataclass
from typing import Generator, Any

from config.mita import MitaProtocol
from database.models import User, Users
from services.backends.base import get_env

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
        rules_base_url: str | None = None,
        mita_config: MitaConfig | None = None,
        hysteria_config: HysteriaConfig | None = None,
        trusttunnel_config: TrustTunnelConfig | None = None) -> str:
    template = env.get_template("config.yaml.j2")
    return template.render(
        domain=domain,
        user=user,
        rules_base_url=rules_base_url,
        mita=mita_config,
        hysteria=hysteria_config,
        trusttunnel=trusttunnel_config
    )


def render_many_configs(
        domain: str,
        users: Users,
        rules_base_url: str | None = None,
        mita_config: MitaConfig | None = None,
        hysteria_config: HysteriaConfig | None = None,
        trusttunnel_config: TrustTunnelConfig | None = None) -> Generator[tuple[uuid.UUID, str], Any, None]:
    for user in users:
        config = render_config(
            domain=domain,
            user=user,
            rules_base_url=rules_base_url,
            mita_config=mita_config,
            hysteria_config=hysteria_config,
            trusttunnel_config=trusttunnel_config)
        yield user.uuid, config

    return None
