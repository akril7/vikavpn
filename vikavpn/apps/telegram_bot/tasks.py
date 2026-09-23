from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from config.app import TZ
from database.connection import Session
from database.crud import get_users_expiring_tomorrow

scheduler = AsyncIOScheduler(timezone=TZ)


async def notify_expiring_subscriptions(bot: Bot) -> None:
    """Отправляет уведомление всем, у кого подписка истекает завтра."""
    async with Session() as session:
        users = await get_users_expiring_tomorrow(session)

    logger.info(f"Subscription notification: {len(users)} users expiring tomorrow")

    for user in users:
        telegram_id = user.telegram_id
        if telegram_id is None:
            continue

        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=(
                    "⚠️ <b>Ваша подписка истекает завтра!</b>\n\n"
                    "Продлите её, чтобы не потерять доступ к сервису."
                ),
            )
        except Exception as e:
            logger.warning(f"Failed to notify user {user.id}: {e}")


def setup_scheduler(bot: Bot) -> None:
    scheduler.add_job(
        notify_expiring_subscriptions,
        trigger=CronTrigger(hour=15, minute=0, timezone=TZ),
        args=[bot],
        id="notify_expiring_subscriptions",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
