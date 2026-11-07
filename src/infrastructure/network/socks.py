import socket

import socks

from loguru import logger


def install_socks_proxy(host: str, port: int) -> None:
    """Глобально направляет все TCP-соединения процесса через SOCKS5.

    Должно вызываться до создания engine и до первых сетевых вызовов.
    Идемпотентно: повторный вызов с теми же аргументами ничего не меняет.
    """
    if getattr(socket.socket, "_vikavpn_socks", False):
        return
    logger.info("Installing global SOCKS5 proxy {}:{}", host, port)
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket
    socket.socket._vikavpn_socks = True
