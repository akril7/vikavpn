import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from loguru import logger

from src.configuration import Settings
from src.configuration.app import PROXY_SOCKS5_ADDRESS
from src.infrastructure.persistence.connection import create_tables

from .handlers import auth, menu, payment, profile, register, renew, start
from .tasks import SubscriptionNotifier


async def main(settings: Settings):
    await create_tables()

    session = None
    if PROXY_SOCKS5_ADDRESS:
        session = AiohttpSession(proxy=f"socks://{PROXY_SOCKS5_ADDRESS}")

    bot = Bot(
        token=settings.telegram_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )

    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(register.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(renew.router)
    dp.include_router(payment.router)

    dp["configuration"] = settings

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
