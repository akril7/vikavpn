from database.models import Users
from services.backends.base import get_env

env = get_env(__file__)


def render_secrets(default_user: str, default_user_uuid: str, users: Users) -> str:
    template = env.get_template("secrets.conf.j2")
    return template.render(
        users=users,
        default_user=default_user,
        default_user_uuid=default_user_uuid
    )
