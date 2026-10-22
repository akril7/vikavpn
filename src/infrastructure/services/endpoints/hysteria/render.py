from src.infrastructure import get_env

env = get_env(__file__)


def render_config(port: int, auth_url: str, mask_url: str) -> str:
    template = env.get_template("server.yaml.j2")
    return template.render(
        port=port,
        auth_url=auth_url,
        mask_url=mask_url
    )


def render_service(
    container_name: str,
    image_name: str,
    config_path: str,
    cert_path: str,
    key_path: str,
) -> str:
    template = env.get_template("service.j2")
    return template.render(
        container_name=container_name,
        image_name=image_name,
        config_path=config_path,
        cert_path=cert_path,
        key_path=key_path,
    )
