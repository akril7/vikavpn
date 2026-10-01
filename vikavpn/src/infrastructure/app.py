import sys

from jinja2 import Environment

from src.infrastructure.systemd import SystemdUnitInstaller, SystemdUnitController
from src.settings.app import BASE_DIR


__env = Environment()
_template = __env.from_string("""
[Unit]
{% if desc %}Description={{ desc }}{% endif %}
After=network.target

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


class AppInstaller(SystemdUnitInstaller):
    def __init__(self, appname: str, desc: str = ""):
        super().__init__(
            service_name=f"vikavpn_{appname}",
            service_file_content=_template.render(
                appname=appname,
                desc=desc,
                work_dir=BASE_DIR,
                executable=sys.executable,
            )
        )


class AppController(SystemdUnitController):
    def __init__(self, appname: str):
        super().__init__(service_name=f"vikavpn_{appname}")
