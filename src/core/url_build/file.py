from urllib.parse import urljoin

from src.db.models import User


def build_origin(domain: str, port: int) -> str:
    return f"https://{domain}" + (f":{port}" if port != 443 else "")


def build_clash_config_url(user: User, origin: str, path: str):
    return urljoin(origin, urljoin(path, user.uuid.hex))


def build_clash_video_guide_url(origin: str):
    return urljoin(origin, "/files/guides/clashmi.mp4")


def build_clash_ads_rules_url(origin: str):
    return urljoin(origin, "/files/clash/rules/ads.yaml")
