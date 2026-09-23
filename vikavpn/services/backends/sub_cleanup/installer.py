import sys

from config.app import BASE_DIR
from config.sub_cleanup import CleanupSettings
from services.backends.base import get_env
from services.backends.systemd import SystemdInstaller


class CleanupInstaller(SystemdInstaller):
    def __init__(self, config: CleanupSettings):
        super().__init__(
            config.service,
            get_env(__file__),
            {
                "work_dir": BASE_DIR,
                "executable": sys.executable,
                "module": "apps.cleanup",
            },
        )
