from jinja2 import Environment, FileSystemLoader

from database.models import Users
from config.app import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "mtproxyl"))


def render_secrets(default_user: str, default_user_uuid: str, users: Users) -> str:
    template = env.get_template("secrets.conf.j2")
    return template.render(
        users=users,
        default_user=default_user,
        default_user_uuid=default_user_uuid
    )
