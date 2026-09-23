import sys

from config.app import BASE_DIR
from config.telegram import TelegramBotSettings
from services.backends.base import get_env
from services.backends.systemd import SystemdInstaller


class TelegramBotInstaller(SystemdInstaller):
    def __init__(self, config: TelegramBotSettings):
        super().__init__(
            config.service,
            get_env(__file__),
            {
                "work_dir": BASE_DIR,
                "executable": sys.executable,
                "module": "apps.telegram_bot",
            },
        )
