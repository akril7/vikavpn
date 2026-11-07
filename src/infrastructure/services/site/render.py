from dataclasses import dataclass

from src.configuration import TLSSettings
from src.infrastructure.templating import get_env

env = get_env(__file__)


@dataclass
class Mount:
    loc: str
    dest: str
    is_proxy: bool = False

    @property
    def location(self) -> str:
        text = self.loc
        if not text.startswith("/"):
            text = "/" + text
        if not text.endswith("/"):
            text = text + "/"
        return text

    @property
    def destination(self) -> str:
        return self.dest.removesuffix("/")


def render_nginx_config(
        http_port: int,
        ssl_port: int,
        root_dir: str,
        mounts: list[Mount],
        tls: TLSSettings,
        http_listen_addr: str | None = None) -> str:
    if http_listen_addr:
        assert ":" not in http_listen_addr

    template = env.get_template("nginx.conf.j2")
    return template.render(
        http_listen_addr=http_listen_addr or False,
        http_port=http_port,
        ssl_port=ssl_port,
        root_dir=root_dir,
        mounts=mounts,
        tls=tls,
    )


def render_stub(text: str) -> str:
    template = env.get_template("stub.html.j2")
    return template.render(text=text)
