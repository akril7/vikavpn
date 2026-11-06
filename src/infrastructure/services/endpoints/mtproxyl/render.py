from src.domain.models import Users
from src.infrastructure.templating import get_env

env = get_env(__file__)


def render_secrets(users: Users) -> str:
    template = env.get_template("secrets.conf.j2")
    return template.render(
        users=users,
    )
