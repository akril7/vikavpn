from config.sub_cleanup import CleanupSettings
from services.backends.systemd import SystemdService


class CleanupService(SystemdService):
    def __init__(self, config: CleanupSettings):
        super().__init__(config.service)
