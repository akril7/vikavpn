import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from src.settings import Settings
from src.db.connection import create_tables

from .handlers import auth, menu, payment, profile, register, renew, start
from .tasks import SubscriptionNotifier


async def main(settings: Settings):
    await create_tables()

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

    dp["settings"] = settings

    notifier = SubscriptionNotifier(bot, settings.telegram_bot)
    await notifier.notify_now()
    notifier.start()

    try:
        logger.info("Telegram bot started (polling)")
        await dp.start_polling(bot)
    finally:
        notifier.shutdown(wait=False)
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main(Settings()))
