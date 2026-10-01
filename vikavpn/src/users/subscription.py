from datetime import timedelta, datetime, UTC

from src.core.utils.dt import utcnow
from src.db.enums import Tariff
from src.db.models import User


def extend(user: User, tariff: Tariff, days: int):
    """ Продлить подписку """
    now = utcnow()
    base = user.sub_expires_at if user.sub_expires_at > now else now
    user.sub_expires_at = base + timedelta(days=days)
    user.proxy_user = True
    user.vpn_user = tariff == Tariff.FULL


async def set_expire(user: User, until: str):
    """Установить срок окончания подписки."""
    user.sub_expires_at = datetime.strptime(until, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
