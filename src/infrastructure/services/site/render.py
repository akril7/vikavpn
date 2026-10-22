from dataclasses import dataclass

from src.settings import TLSSettings
from src.infrastructure import get_env

env = get_env(__file__)


@dataclass
class Mount:
    location: str
    destination: str
    is_proxy: bool = False


def render_nginx_config(
        port: int,
        extra_ports: list[int],
        root_dir: str,
        mounts: list[Mount],
        tls: TLSSettings) -> str:
    template = env.get_template("nginx.conf.j2")
    return template.render(
        port=port,
        extra_ports=extra_ports,
        root_dir=root_dir,
        mounts=mounts,
        tls=tls,
    )


def render_index_html(title: str) -> str:
    template = env.get_template("index.html.j2")
    return template.render(title=title)
