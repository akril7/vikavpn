from config.mita import MitaSettings
from services.base import Service, ServiceError
from utils.subprocess import run_and_get_text, run_with_check
from utils.systemctl import SystemdService


class MitaService(Service):
    def __init__(self, config: MitaSettings):
        self.__service = SystemdService(config.service)

    @property
    def status(self) -> bool:
        return "RUNNING" in run_and_get_text(["mita", "status"])

    def start(self):
        if self.status:
            return

        output = run_and_get_text(["mita", "start"])
        if "proxy is started" not in output:
            raise ServiceError(output)

    def stop(self):
        if not self.status:
            return

        run_with_check(["mita", "stop"])

    def restart(self):
        self.stop()
        self.start()
