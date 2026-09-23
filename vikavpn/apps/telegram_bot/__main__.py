import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from config.telegram import TelegramBotSettings
from database.connection import create_tables

from .handlers import auth, menu, payment, profile, register, renew, start
from .tasks import scheduler, setup_scheduler


async def main():
    config = TelegramBotSettings()

    await create_tables()

    bot = Bot(
        token=config.token,
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

    setup_scheduler(bot)

    logger.info("Telegram bot started (polling)")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
