from src.application.ports.services.callables import IsInstallCallback
from src.application.services import BaseController
from src.configuration import MTProxyLSettings
from src.infrastructure.system.subprocess import run_with_check, run_and_get_text, check_root


class MTProxyLController(BaseController):
    def __init__(self, mtproxyl: MTProxyLSettings, is_install_callback: IsInstallCallback):
        super().__init__(is_install_callback)
        self.__default_user = mtproxyl.default_user

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
        run_with_check(["mtproxyl", "secret", "enable", self.__default_user])
