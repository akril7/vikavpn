from src.application.services import BaseInstaller
from src.configuration import MicrowarpSettings
from src.infrastructure.system.docker import container_exists
from src.infrastructure.system.subprocess import deb_is_installed, run_with_check


class MicrowarpInstaller(BaseInstaller):
    def __init__(self, microwarp: MicrowarpSettings):
        self.__image = microwarp.image
        self.__container_name = microwarp.container_name
        self.__port = microwarp.port

    @property
    def is_installed(self) -> bool:
        return deb_is_installed("docker") and container_exists(self.__container_name)

    def _install(self):
        run_with_check([
            "docker", "run", "-d",
            "--name", self.__container_name,
            "--restart", "always",
            "-p", f"127.0.0.1:{self.__port}:1080",
            "--cap-add", "NET_ADMIN",
            "--cap-add", "SYS_MODULE",
            "--sysctl", "net.ipv4.conf.all.src_valid_mark=1",
            "-e", "ALLOW_NO_AUTH = 1",
            "-v", "warp-data:/etc/wireguard",
            self.__image
        ])

    def _uninstall(self):
        run_with_check(["docker", "stop", self.__container_name])
        run_with_check(["docker", "rm", self.__container_name])
        run_with_check(["docker", "image rm", self.__image])
