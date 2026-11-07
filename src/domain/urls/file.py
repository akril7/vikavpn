import os.path
from pathlib import Path
from urllib.parse import urljoin, urlparse

from src.domain.models import User


def get_file_name(url: str) -> str:
    return Path(urlparse(url).path).name


def build_origin(domain: str, port: int) -> str:
    return f"https://{domain}" + (f":{port}" if port != 443 else "")


def build_clash_config_url(user: User, origin: str, path: str):
    return urljoin(origin, urljoin(path, user.uuid.hex))


def build_clash_video_guide_url(origin: str):
    file_path = "files/guides/clashmi.mp4"
    if not os.path.exists(file_path):
        raise RuntimeError(f"Cannot locate {file_path}")

    return urljoin(origin, "/" + file_path)
