import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from src.apps.telegram_bot.tasks import notify_expiring_subscriptions
from src.infrastructure.manager.configure import build_reloader
from src.infrastructure.manager.registry import Registry
from src.settings import Settings
from src.db.connection import create_tables

from .handlers import auth, menu, payment, profile, register, renew, start
from . import tasks


async def main(settings: Settings):
    await create_tables()

    registry = Registry(settings)
    reloader = build_reloader(registry)

    bot = Bot(
        token=settings.telegram_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(register.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(renew.router)
    dp.include_router(payment.router)
    dp.workflow_data.update(settings=settings)
    dp.workflow_data.update(reloader=reloader)

    await notify_expiring_subscriptions(bot)
    tasks.setup_scheduler(bot, settings.telegram_bot)

    try:
        logger.info("Telegram bot started (polling)")
        reloader.start()
        await dp.start_polling(bot)
    finally:
        if tasks.scheduler.running:
            tasks.scheduler.shutdown()

        await reloader.stop()


if __name__ == "__main__":
    asyncio.run(main(Settings()))
