from database.models import Users
from settings.mita import MitaProtocol
from services.backends.base import get_env


class PortBindingsItem:
    def __init__(self,
                 protocol: MitaProtocol,
                 port: int | None = None,
                 port_range: str | None = None):
        if port is not None and port_range is None:
            self.port = port
        elif port_range is not None and port is None:
            p1, p2 = port_range.split('-')
            if not (p1.isdigit() and p2.isdigit()):
                raise ValueError("port_range error format")

            self.port_range = port_range
        else:
            raise ValueError("Fill only port or only port_range")

        self.protocol = str(protocol)


PortBindings = list[PortBindingsItem]

env = get_env(__file__)


def render_config(port_bindings: PortBindings, users: Users) -> str:
    template = env.get_template("mita.json.j2")
    return template.render(port_bindings=port_bindings, users=users)
