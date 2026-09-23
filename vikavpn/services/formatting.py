from datetime import datetime, UTC

from config.app import TZ
from database.models import User


def as_aware(dt: datetime) -> datetime:
    """SQLite теряет tzinfo — возвращаем aware по TZ проекта."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt


def format_date(dt: datetime) -> str:
    return as_aware(dt).strftime("%d.%m.%Y")


def format_subscription_info(user: User) -> str:
    is_active = user.is_active
    days_left = (user.sub_expires_at.date() - datetime.now(UTC).date()).days
    status = "активна" if is_active else "неактивна"
    return (
        f"👤 Имя: {user.name}\n\n"
        f"📊 Статус: {status}\n\n"
        f"🎁 Тариф: {_tariff_label(user)}\n\n"
        f"📅 Подписка до: {format_date(user.sub_expires_at)} ({f"{days_left} дней" if days_left >= 0 else "истекла"})"
    )


def _tariff_label(user: User) -> str:
    if user.vpn_user and user.proxy_user:
        return "VPN + TG Proxy"
    if user.vpn_user:
        return "VPN"
    if user.proxy_user:
        return "TG Proxy"
    return "—"
