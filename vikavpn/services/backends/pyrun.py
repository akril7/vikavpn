import sys

from jinja2 import Environment

from services.backends.systemd import SystemdInstaller
from settings.app import BASE_DIR

__SERVICE_TEMPLATE = """
[Unit]
Description={{ desc }}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={{ work_dir }}
ExecStart={{ executable }} -m apps.{{ appname }}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

__env = Environment()
_template = __env.from_string(__SERVICE_TEMPLATE)


class AppInstaller(SystemdInstaller):
    def __init__(self, appname: str, desc: str, service_name: str):
        super().__init__(
            service_name=service_name,
            service_file_content=_template.render(
                appname=appname,
                desc=desc,
                work_dir=BASE_DIR,
                executable=sys.executable,
            )
        )
