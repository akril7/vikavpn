from config.tls import TLSSettings
from database.models import Users
from services.backends.base import get_env

env = get_env(__file__)


def render_hosts(hostname: str, tls: TLSSettings, allowed_sni: list[str]) -> str:
    template = env.get_template("hosts.toml.j2")
    return template.render(
        hostname=hostname,
        cert_path=tls.cert_path,
        key_path=tls.key_path,
        allowed_sni=allowed_sni
    )


def render_settings(port: int, metrics_port: int | None = None) -> str:
    template = env.get_template("vpn.toml.j2")
    return template.render(
        port=port,
        metrics_port=metrics_port
    )


def render_users_config(users: Users) -> str:
    template = env.get_template("credentials.toml.j2")
    return template.render(users=users)
