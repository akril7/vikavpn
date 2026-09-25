from services.backends.base import Service
from services.system.subprocess import run_with_check, run_and_get_text


class MTProxyLService(Service):
    @property
    def status(self) -> bool:
        return '"status":"running"' in run_and_get_text(["mtproxyl", "status", "--json"])

    def start(self):
        run_with_check(["mtproxyl", "start"])

    def stop(self):
        run_with_check(["mtproxyl", "stop"])

    def restart(self):
        run_with_check(["mtproxyl", "restart"])
