from src.application.ports.services import ControllerError
from src.application.services import BaseController
from src.infrastructure.system.subprocess import run_and_get_text, run_with_check


class MitaController(BaseController):
    @property
    def _status(self) -> bool:
        return "RUNNING" in run_and_get_text(["mita", "status"])

    def start(self):
        output = run_and_get_text(["mita", "start"])
        if "proxy is started" not in output:
            raise ControllerError(output)

    def stop(self):
        run_with_check(["mita", "stop"])

    def restart(self):
        self.stop()
        self.start()

    def _reload(self):
        output = run_and_get_text(["mita", "reload"])
        if "server is reloaded" not in output:
            raise ControllerError(output)
