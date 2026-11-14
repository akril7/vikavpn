from dataclasses import dataclass
from datetime import datetime

from src.domain.models import User
from src.domain.utils.dt import utcnow
from src.configuration import Settings
from src.configuration.app import TZ
from src.application.urls import build_clash_config_url, build_telegram_proxy_url, build_bot_auth_url


@dataclass(frozen=True)
class ProfileView:
    name: str
    uuid_hex: str
    password: str
    expires_at: datetime
    is_active: bool
    days_left: int
    tariff_label: str
    telegram_id: int
    clash_url: str | None
    tg_proxy_url: str | None
    bot_auth_url: str | None


def tariff_label(user: User) -> str:
    if user.vpn_user and user.proxy_user:
        return "VPN + TG Proxy"
    if user.vpn_user:
        return "VPN"
    if user.proxy_user:
        return "TG Proxy"
    return "—"


def build_profile(user: User, settings: Settings) -> ProfileView:
    """
    Собрать представление профиля пользователя для отображения.
    Требует загрузки messenger у user
    """

    now = utcnow()
    days_left = max(0, (user.sub_expires_at.date() - now.date()).days)

    clash_url = build_clash_config_url(settings, user) if user.vpn_user else None
    tg_proxy_url = build_telegram_proxy_url(settings, user) if user.proxy_user else None
    bot_auth_url = build_bot_auth_url(settings, user)

    return ProfileView(
        name=user.name,
        uuid_hex=user.uuid.hex,
        password=user.password,
        expires_at=user.sub_expires_at.astimezone(TZ),
        is_active=user.is_active,
        days_left=days_left,
        tariff_label=tariff_label(user),
        telegram_id=user.telegram_id,
        clash_url=clash_url,
        tg_proxy_url=tg_proxy_url,
        bot_auth_url=bot_auth_url
    )
