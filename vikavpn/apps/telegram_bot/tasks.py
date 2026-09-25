import asyncio
from datetime import UTC

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from settings import telegram_bot
from database.connection import Session
from database.repo.user import UserRepository

scheduler = AsyncIOScheduler(timezone=UTC)


async def notify_expiring_subscriptions(bot: Bot) -> None:
    """Отправляет уведомление всем, у кого подписка истекает завтра."""
    async with Session() as session:
        repo = UserRepository(session)
        users = await repo.list_expiring_within(hours=24)

    logger.info(f"Subscription notification: {len(users)} users expiring tomorrow")

    for user in users:
        telegram_id = user.telegram_id
        if telegram_id is None:
            continue

        await bot.send_message(
            chat_id=telegram_id,
            text=(
                "⚠️ <b>Ваша подписка истекает завтра!</b>\n\n"
                "Продлите её, чтобы не потерять доступ к сервису."
            )
        )

        await asyncio.sleep(0.2)


def setup_scheduler(bot: Bot) -> None:
    scheduler.add_job(
        notify_expiring_subscriptions,
        trigger=CronTrigger(hour=telegram_bot.expire_notif_hour,
                            minute=telegram_bot.expire_notif_minute),
        args=[bot],
        id="notify_expiring_subscriptions",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
