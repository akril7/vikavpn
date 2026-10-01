import shutil

from src.core.interfaces.controller import Controller
from src.infrastructure.system.subprocess import run_with_check, run_and_get_text, check_root
from src.settings import MTProxyLSettings


def _is_installed() -> bool:
    return shutil.which("mtproxyl") is not None


class MTProxyLController(Controller):
    def __init__(self, mtproxyl: MTProxyLSettings):
        self.__default_user = mtproxyl.default_user

    @property
    def status(self) -> bool:
        check_root()
        return _is_installed() and '"status":"running"' in run_and_get_text(["mtproxyl", "status", "--json"])

    def start(self):
        check_root()
        run_with_check(["mtproxyl", "start"])

    def stop(self):
        check_root()
        run_with_check(["mtproxyl", "stop"])

    def restart(self):
        check_root()
        run_with_check(["mtproxyl", "restart"])

    def reload(self):
        check_root()
        run_with_check(["mtproxyl", "secret", "enable", self.__default_user])
