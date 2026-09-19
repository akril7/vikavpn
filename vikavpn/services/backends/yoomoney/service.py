from config.yoomoney import YoomoneySettings
from services.backends.systemd import SystemdService


class YoomoneyService(SystemdService):
    def __init__(self, config: YoomoneySettings):
        super().__init__(config.webhook_service)
