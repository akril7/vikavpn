from src.infrastructure import get_env

env = get_env(__file__)


def render_config(
        hostname: str,
        port: int,
        username: str,
        password: str,
        use_http2_proto: bool,
        socks5_address: str) -> str:
    template = env.get_template("config.toml.j2")
    return template.render(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        protocol="http2" if use_http2_proto else "http3",
        socks5_address=socks5_address,
    )


def render_service(work_dir: str) -> str:
    template = env.get_template("service.j2")
    return template.render(work_dir=work_dir)
