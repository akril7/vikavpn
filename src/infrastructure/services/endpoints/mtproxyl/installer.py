import os
import shutil
from pathlib import Path

from loguru import logger

from src.settings import MTProxyLSettings, TLSSettings
from src.core.interfaces import Installer
from src.infrastructure.system.subprocess import check_root, run_pty_proc, run_with_check
from src.core.utils.file import download_file


class MTProxyLInstaller(Installer):
    def __init__(self, mtproxyl: MTProxyLSettings, tls: TLSSettings):
        self.__install_script_link = mtproxyl.install_script_link
        self.__selfmask_template = mtproxyl.selfmask_template
        self.__socks5_upstream_address = mtproxyl.socks5_upstream_address
        self.__domain = tls.domain
        if mtproxyl.subdomain:
            self.__domain = mtproxyl.subdomain + "." + self.__domain

    @property
    def is_installed(self) -> bool:
        return shutil.which("mtproxyl") is not None

    def _install(self):
        check_root()

        script_path = Path("/tmp/mtproxyl-install.sh")

        logger.debug("Get mtproxyl install script")
        download_file(self.__install_script_link, script_path)

        logger.debug("Run mtproxyl install script")
        cmd = [
            "sudo", "bash", script_path, "--",
            "--web-domain", self.__domain,
            "--selfmask-template", self.__selfmask_template,
            "--mode", "manager",
            "--engine", "binary",
            "--engine-version", "3.5.14",
            "--service-name", "standard",
            "--proxy-mode", "web",
            "--port", "443",
            "--mask", "off",
            "--sni-policy", "reject_handshake",
            "--meko", "no",
            "--web", "yes",
            "--web-layout", "shared",
            "--web-frontend", "nginx",
            "--web-carrier", "https",
            "--web-carriers", "websocket-lanes,https-lanes,websocket",
            "--web-secret-mode", "dd",
            "--web-port", "443",
        ]

        master, proc = run_pty_proc(cmd)
        proc.wait()
        os.close(master)

        if self.__socks5_upstream_address:
            logger.debug("Setup socks5 upstream")
            run_with_check(["mtproxyl", "upstream", "add", "proxy", "socks5", self.__socks5_upstream_address])
            run_with_check(["mtproxyl", "upstream", "remove", "direct"])

    def _uninstall(self):
        logger.debug("Run mtproxyl uninstall command")
        master, proc = run_pty_proc(["mtproxyl", "uninstall"])
        os.write(master, "yes\n\n\n".encode())
        proc.wait()
        os.close(master)
