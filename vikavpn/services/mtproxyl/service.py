from services.base import Service
from utils.subprocess import run_with_check, run_and_get_text


class MTProxyLService(Service):
    @property
    def status(self) -> bool:
        return "РАБОТАЕТ" in run_and_get_text(["mtproxyl", "status"])

    def start(self):
        run_with_check(["mtproxyl", "start"])

    def stop(self):
        run_with_check(["mtproxyl", "stop"])

    def restart(self):
        run_with_check(["mtproxyl", "restart"])
