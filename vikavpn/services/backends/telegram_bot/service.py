from config.telegram import TelegramBotSettings
from services.backends.systemd import SystemdService


class TelegramBotService(SystemdService):
    def __init__(self, config: TelegramBotSettings):
        super().__init__(config.service)
