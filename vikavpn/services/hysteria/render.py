from jinja2 import Environment, FileSystemLoader

from database.models import Users
from config.app import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR / "hysteria"))


def render_config(port: int, users: Users, mask_url: str) -> str:
    template = env.get_template("hysteria.yaml.j2")
    return template.render(port=port, users=users, mask_url=mask_url)
