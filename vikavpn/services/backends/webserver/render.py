from typing import Sequence

from config.tls import TLSSettings
from config.webserver import Mounts, ProxyPasses
from services.backends.base import get_env

env = get_env(__file__)


def render_nginx_config(
        ports: Sequence[int],
        web_root: str,
        mounts: Mounts = None,
        proxy_passes: ProxyPasses = None,
        tls: TLSSettings | None = None) -> str:
    template = env.get_template("nginx.conf.j2")
    return template.render(
        ports=ports,
        web_root=web_root,
        mounts=mounts or [],
        proxy_passes=proxy_passes or [],
        tls=tls,
    )


def render_index_html(title: str) -> str:
    template = env.get_template("index.html.j2")
    return template.render(title=title)
