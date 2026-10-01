import secrets

from src.settings import TLSSettings
from src.db.models import Users
from src.infrastructure import get_env

env = get_env(__file__)


def render_hosts(tls: TLSSettings, allowed_sni: list[str]) -> str:
    template = env.get_template("hosts.toml.j2")
    return template.render(
        hostname=tls.domain,
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


def render_users(users: Users) -> str:
    template = env.get_template("credentials.toml.j2")
    return template.render(
        users=users,
        default_user=secrets.token_hex(4)
    )


def render_service(work_dir: str) -> str:
    template = env.get_template("service.j2")
    return template.render(work_dir=work_dir)
