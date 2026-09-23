import os
import shutil
from pathlib import Path

from loguru import logger

from config.app import SNI
from config.mtproxyl import MTProxyLSettings
from config.tls import TLSSettings
from services.backends.base import Installer
from services.download import download_file
from services.system.subprocess import check_root, run_pty_proc


class MTProxyLInstaller(Installer):
    def __init__(self, mtproxyl_config: MTProxyLSettings, tls_config: TLSSettings):
        self.__install_script_link = mtproxyl_config.install_script_link
        self.__mode = mtproxyl_config.mode
        self.__port = mtproxyl_config.port
        self.__use_zapret2 = mtproxyl_config.use_zapret2
        self.__default_user = mtproxyl_config.default_user
        self.__default_user_uuid = mtproxyl_config.default_user_uuid
        self.__domain = tls_config.domain

    @property
    def name(self) -> str:
        return "mtproxyl"

    @property
    def is_installed(self) -> bool:
        return shutil.which("mtproxyl") is not None

    def _install(self, force: bool = False):
        if self.is_installed and not force:
            logger.info("mtproxyl already installed")

        check_root()

        script_path = Path("/tmp/mtproxyl-install.sh")

        logger.info("Get mtproxyl install script")
        download_file(self.__install_script_link, script_path)

        logger.info("Run mtproxyl install script")
        cmd = ["sudo", "bash", script_path, "--",
               "--mode", str(self.__mode),
               "--port", str(self.__port),
               "--host", self.__domain,
               "--sni", SNI,
               "--secret", f"{self.__default_user}:{self.__default_user_uuid}",
               "--zapret2", "yes" if self.__use_zapret2 else "no"]
        if force:
            cmd.append("--force")

        master, proc = run_pty_proc(cmd)
        proc.wait()
        os.close(master)

    def _uninstall(self):
        if not self.is_installed:
            logger.info("mtproxyl installation not founed")
            return

        logger.info("Run mtproxyl uninstall command")
        master, proc = run_pty_proc(["mtproxyl", "uninstall"])
        os.write(master, "yes\n\n".encode())
        proc.wait()
        os.close(master)
