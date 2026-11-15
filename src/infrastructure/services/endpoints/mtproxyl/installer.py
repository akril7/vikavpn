import shutil
from pathlib import Path

from loguru import logger

from src.configuration import MTProxyLSettings, TLSSettings, ProxySettings, SiteSettings
from src.application.services import BaseInstaller
from src.infrastructure.system.subprocess import check_root, run_pty_proc, run_with_check, deb_is_installed
from src.infrastructure.utils.file import download_file

from .render import render_nginx_conf


class MTProxyLInstaller(BaseInstaller):
    def __init__(self, mtproxyl: MTProxyLSettings, tls: TLSSettings, proxy: ProxySettings, site: SiteSettings):
        self.__install_script_link = mtproxyl.install_script_link
        self.__socks5_upstream_address = proxy.address
        self.__tls = tls
        self.__domain = tls.domain
        if mtproxyl.subdomain:
            self.__domain = mtproxyl.subdomain + "." + self.__domain

        self.__nginx_conf = render_nginx_conf(
            tls=tls,
            proxy_domain=self.__domain,
            site_http_port=site.http_port
        )

    @property
    def is_installed(self) -> bool:
        return shutil.which("mtproxyl") is not None

    def _install(self):
        check_root()

        script_path = Path("/tmp/mtproxyl-install.sh")

        logger.debug("Get mtproxyl install script")
        download_file(self.__install_script_link, script_path)

        logger.debug("Stop system nginx")
        if deb_is_installed("nginx"):
            run_with_check(["systemctl", "stop", "nginx"])

        logger.debug("Run mtproxyl install script")
        run_pty_proc(command=[
            "sudo", "bash", script_path, "--",
            "--web-domain", self.__domain,
            "--mode", "manager",
            "--engine", "binary",
            "--engine-version", "3.5.14",
            "--service-name", "standard",
            "--proxy-mode", "web",
            "--port", "443",
            "--mask", "off",
            "--meko", "no",
            "--web", "yes",
            "--web-layout", "shared",
            "--web-frontend", "nginx",
            "--web-carrier", "https",
            "--web-carriers", "websocket-lanes,https-lanes,websocket",
            "--web-secret-mode", "dd",
            "--web-port", "443",
        ])

        Path("/opt/mtproxyl/nginx-custom.conf").write_text(self.__nginx_conf)

        run_pty_proc(
            command=["mtproxyl", "web", "nginx-config", "on"],
            write_text="y\n"
        )

        if self.__socks5_upstream_address:
            logger.debug("Setup socks5 upstream")
            run_with_check(["mtproxyl", "upstream", "add", "proxy", "socks5", self.__socks5_upstream_address])
            run_with_check(["mtproxyl", "upstream", "remove", "direct"])

        logger.debug("Start system nginx")
        if deb_is_installed("nginx"):
            run_with_check(["systemctl", "start", "nginx"])

    def _uninstall(self):
        logger.debug("Run mtproxyl uninstall command")
        run_pty_proc(
            command=["mtproxyl", "uninstall"],
            write_text="yes\n\n\n",
            timeout=20.0
        )
