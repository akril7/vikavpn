from src.configuration import TLSSettings
from src.domain.models import Users
from src.infrastructure.templating import get_env

env = get_env(__file__)


def render_secrets(users: Users) -> str:
    template = env.get_template("secrets.conf.j2")
    return template.render(
        users=users,
    )


def render_nginx_conf(
        tls: TLSSettings,
        proxy_domain: str,
        site_http_port: int,
) -> str:
    template = env.get_template("nginx.conf.j2")
    return template.render(
        proxy_domain=proxy_domain,
        # mtproxyl use letsencrypt for new certs
        proxy_cert_path=f"/etc/letsencrypt/live/{proxy_domain}/fullchain.pem",
        proxy_key_path=f"/etc/letsencrypt/live/{proxy_domain}/privkey.pem",
        domain=tls.domain,
        cert_path=tls.cert_path,
        key_path=tls.key_path,
        site_http_port=site_http_port
    )
