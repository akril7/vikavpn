import sys

from jinja2 import Environment

from src.infrastructure.systemd import SystemdUnitInstaller, SystemdUnitController
from src.settings.app import BASE_DIR

SERVICE_PREFIX = "vikavpn-"

__env = Environment()
_template = __env.from_string("""
[Unit]
{% if desc %}Description={{ desc }}{% endif %}
After=network.target
{{ extra_unit_lines }}

[Service]
Type=simple
User=root
WorkingDirectory={{ work_dir }}
ExecStart={{ executable }} -m src.apps.{{ appname }}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
""")


def format_service_name(appname: str):
    appname = appname.replace('_', '-')

    if not appname.startswith(SERVICE_PREFIX):
        appname = SERVICE_PREFIX + appname

    return appname


class AppInstaller(SystemdUnitInstaller):
    def __init__(self, appname: str, desc: str = "", requires: list[str] | None = None):
        extra = []
        if requires:
            for s in requires:
                s = format_service_name(s)
                extra.append(f"Requires={s}.service")
                extra.append(f"After={s}.service")
                extra.append(f"BindsTo={s}.service")

        super().__init__(
            service_name=format_service_name(appname),
            service_file_content=_template.render(
                appname=appname,
                desc=desc,
                work_dir=BASE_DIR,
                executable=sys.executable,
                extra_unit_lines="\n".join(extra),
            ),
        )


class AppController(SystemdUnitController):
    def __init__(self, appname: str):
        super().__init__(service_name=format_service_name(appname))
