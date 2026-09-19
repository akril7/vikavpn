from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Tariff, User


async def extend_subscription(
    session: AsyncSession,
    user: User,
    tariff: Tariff,
    days: int,
) -> None:
    now = datetime.now()
    if user.sub_expires_at > now:
        user.sub_expires_at = user.sub_expires_at + timedelta(days=days)
    else:
        user.sub_expires_at = now + timedelta(days=days)

    user.proxy_user = True
    user.vpn_user = (tariff == Tariff.FULL)

    await session.commit()
