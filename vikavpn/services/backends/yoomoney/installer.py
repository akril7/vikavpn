import sys

from config.app import BASE_DIR
from config.yoomoney import YoomoneySettings
from services.backends.base import get_env
from services.backends.systemd import SystemdInstaller


class YoomoneyInstaller(SystemdInstaller):
    def __init__(self, config: YoomoneySettings):
        super().__init__(config.webhook_service, get_env(__file__),
                         {
                             "work_dir": BASE_DIR,
                             "executable": sys.executable
                         })
