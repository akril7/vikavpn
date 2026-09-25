from dataclasses import dataclass
from datetime import datetime

from database.models import User
from settings import webserver, clash, tls, mtproxyl
from settings.app import TZ, SNI
from utils.datetime import utcnow
from services.url_build import build_clash_config_url, build_telegram_proxy_url


@dataclass(frozen=True)
class ProfileView:
    name: str
    password: str
    expires_at: datetime
    is_active: bool
    days_left: int
    tariff_label: str
    clash_url: str | None
    tg_proxy_url: str | None
    managed_names: list[str]


def tariff_label(user: User) -> str:
    if user.vpn_user and user.proxy_user:
        return "VPN + TG Proxy"
    if user.vpn_user:
        return "VPN"
    if user.proxy_user:
        return "TG Proxy"
    return "—"


def build_profile(user: User,) -> ProfileView:
    now = utcnow()
    days_left = (user.sub_expires_at.date() - now.date()).days

    clash_url = build_clash_config_url(user, webserver.server, clash.url_config_path) if user.vpn_user else None

    tg_proxy_url = build_telegram_proxy_url(user, SNI, tls.domain, mtproxyl.port) if user.proxy_user else None

    managed_names = [u.managed.name for u in user.managed_links]

    return ProfileView(
        name=user.name,
        password=user.password,
        expires_at=user.sub_expires_at.astimezone(TZ),
        is_active=user.is_active,
        days_left=days_left,
        tariff_label=tariff_label(user),
        clash_url=clash_url,
        tg_proxy_url=tg_proxy_url,
        managed_names=managed_names,
    )
