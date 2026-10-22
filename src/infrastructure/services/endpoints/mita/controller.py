from src.core.interfaces.controller import Controller
from src.core.interfaces import ControllerError
from src.infrastructure.system.subprocess import run_and_get_text, run_with_check


class MitaController(Controller):
    @property
    def status(self) -> bool:
        return "RUNNING" in run_and_get_text(["mita", "status"])

    def start(self):
        if self.status:
            return

        output = run_and_get_text(["mita", "start"])
        if "proxy is started" not in output:
            raise ControllerError(output)

    def stop(self):
        if not self.status:
            return

        run_with_check(["mita", "stop"])

    def restart(self):
        self.stop()
        self.start()

    def reload(self):
        output = run_and_get_text(["mita", "reload"])
        if "server is reloaded" not in output:
            raise ControllerError(output)
