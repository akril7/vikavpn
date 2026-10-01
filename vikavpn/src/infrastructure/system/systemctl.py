from pathlib import Path

from .subprocess import run_with_check, run_without_out


class ServiceNotExistsError(Exception):
    pass


def check_exists(func):
    def wrapper(service: "SystemdUnit", *args, **kwargs):
        if not service.exists():
            raise ServiceNotExistsError(service.name)

        return func(self=service, *args, **kwargs)

    return wrapper


class SystemdUnit:
    def __init__(self, name: str):
        self.__name = name
        self.__path = Path(f"/etc/systemd/system/{name}.service")

    @property
    def name(self) -> str:
        return self.__name

    @check_exists
    def start(self):
        run_with_check(["systemctl", "start", self.name])

    @check_exists
    def stop(self):
        run_with_check(["systemctl", "stop", self.name])

    @check_exists
    def restart(self):
        run_with_check(["systemctl", "restart", self.name])

    @check_exists
    def reload(self):
        if not self.status():
            self.start()

        run_with_check(["systemctl", "reload", self.name])

    @check_exists
    def reload_or_restart(self):
        run_with_check(["systemctl", "reload-or-restart", self.name])

    @check_exists
    def kill(self, signal: str):
        run_with_check(["systemctl", "kill", "-s", signal, self.name])

    @check_exists
    def status(self) -> bool:
        return run_without_out(["systemctl", "is-active", self.name]).returncode == 0

    @check_exists
    def enable(self):
        run_without_out(["systemctl", "enable", self.name], check=True)

    @check_exists
    def disable(self):
        run_with_check(["systemctl", "disable", self.name])

    def write_config(self, config: str):
        self.__path.write_text(config)

    def remove(self):
        self.__path.unlink()

    def exists(self) -> bool:
        return run_without_out(['systemctl', 'cat', f'{self.name}.service']).returncode == 0


def daemon_reload():
    run_with_check(["systemctl", "daemon-reload"])
