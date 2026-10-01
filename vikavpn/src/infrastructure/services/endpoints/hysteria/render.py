from src.infrastructure import get_env

env = get_env(__file__)


def render_config(port: int, auth_url: str, mask_url: str) -> str:
    template = env.get_template("server.yaml.j2")
    return template.render(
        port=port,
        auth_url=auth_url,
        mask_url=mask_url
    )
