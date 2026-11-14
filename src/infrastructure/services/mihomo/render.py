from src.infrastructure.templating import get_env

env = get_env(__file__)


def render_config(
        hostname: str,
        port: int,
        username: str,
        password: str,
        quic: bool,
        proxy_port: int,
        ctrl_port: int,
        ctrl_secret: str,
        direct_rule_domain: str) -> str:
    template = env.get_template("config.yaml.j2")
    return template.render(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        quic=quic,
        proxy_port=proxy_port,
        ctrl_port=ctrl_port,
        secret=ctrl_secret,
        direct_rule_domain=direct_rule_domain,
    )
