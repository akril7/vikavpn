from database.models import Users
from services.backends.base import get_env

env = get_env(__file__)


def render_config(port: int, users: Users, mask_url: str) -> str:
    template = env.get_template("server.yaml.j2")
    return template.render(port=port, users=users, mask_url=mask_url)
