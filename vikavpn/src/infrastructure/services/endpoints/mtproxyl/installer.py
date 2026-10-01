import os
import shutil
from pathlib import Path

from loguru import logger

from src.settings import MTProxyLSettings, TLSSettings
from src.core.interfaces import Installer
from src.infrastructure.system.subprocess import check_root, run_pty_proc
from src.core.utils.file import download_file


class MTProxyLInstaller(Installer):
    def __init__(self, mtproxyl: MTProxyLSettings, tls: TLSSettings):
        self.__install_script_link = mtproxyl.install_script_link
        self.__mode = mtproxyl.mode
        self.__port = mtproxyl.port
        self.__sni = mtproxyl.sni
        self.__use_zapret2 = mtproxyl.use_zapret2
        self.__default_user = mtproxyl.default_user
        self.__default_user_uuid = mtproxyl.default_user_uuid
        self.__domain = tls.domain

    @property
    def is_installed(self) -> bool:
        return shutil.which("mtproxyl") is not None

    def _install(self):
        check_root()

        script_path = Path("/tmp/mtproxyl-install.sh")

        logger.info("Get mtproxyl install script")
        download_file(self.__install_script_link, script_path)

        logger.info("Run mtproxyl install script")
        cmd = ["sudo", "bash", script_path, "--",
               "--mode", str(self.__mode),
               "--port", str(self.__port),
               "--host", self.__domain,
               "--sni", self.__sni,
               "--meko", "no",
               "--secret", f"{self.__default_user}:{self.__default_user_uuid}",
               "--zapret2", "yes" if self.__use_zapret2 else "no"]

        master, proc = run_pty_proc(cmd)
        proc.wait()
        os.close(master)

    def _uninstall(self):
        logger.info("Run mtproxyl uninstall command")
        master, proc = run_pty_proc(["mtproxyl", "uninstall"])
        os.write(master, "yes\n\n".encode())
        proc.wait()
        os.close(master)
