from src.application.services import BaseController
from src.infrastructure.system.subprocess import run_with_check, run_and_get_text, check_root


class MTProxyLController(BaseController):
    @property
    def _status(self) -> bool:
        check_root()
        return '"status":"running"' in run_and_get_text(["mtproxyl", "status", "--json"])

    def start(self):
        check_root()
        run_with_check(["mtproxyl", "start"])

    def stop(self):
        check_root()
        run_with_check(["mtproxyl", "stop"])

    def restart(self):
        check_root()
        run_with_check(["mtproxyl", "restart"])

    def _reload(self):
        check_root()
        run_with_check(["mtproxyl", "secret", "enable", "default"])
