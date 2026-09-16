from typing import Sequence

from jinja2 import Environment, FileSystemLoader

from config.app import TEMPLATE_DIR
from config.webserver import Mounts
from utils import SSLPaths

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "webserver"))


def render_nginx_config(
        ports: Sequence[int],
        web_root: str,
        mounts: Mounts = None,
        ssl_paths: SSLPaths | None = None) -> str:
    template = env.get_template("nginx.conf.j2")
    return template.render(
        ports=ports,
        web_root=web_root,
        mounts=mounts or [],
        use_ssl=ssl_paths is not None,
        cert_path=ssl_paths.cert if ssl_paths else None,
        key_path=ssl_paths.key if ssl_paths else None
    )


def render_index_html(title: str) -> str:
    template = env.get_template("index.html.j2")
    return template.render(title=title)
