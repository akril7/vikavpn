from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from database.models import Users
from config.app import TEMPLATE_DIR
from utils import SSLPaths

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "trusttunnel"))


def render_hosts(hostname: str, ssl_paths: SSLPaths, allowed_sni: list[str]) -> str:
    template = env.get_template("hosts.toml.j2")
    return template.render(
        hostname=hostname,
        cert_path=ssl_paths.cert,
        key_path=ssl_paths.key,
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


def render_service_config(work_dir: Path):
    return env.get_template("trusttunnel.service.j2").render(work_dir=work_dir)
