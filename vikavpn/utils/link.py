import os.path

from database.models import User


def generate_telegram_proxy_link(user: User, sni: str, server: str, port: int) -> str:
    uuid = user.uuid.hex
    sni = sni.encode().hex()

    return f"tg://proxy?server={server}&port={port}&secret=ee{uuid}{sni}"


def generate_clash_config_link(user: User, server: str, path: str, use_ssl: bool = True):
    return f"{"https" if use_ssl else "http"}://{server}/{os.path.join(path, user.uuid.hex)}"
