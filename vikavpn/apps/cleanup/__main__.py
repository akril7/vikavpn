import asyncio
from datetime import UTC

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from settings import cleanup
from services.core.commands import reload_users
from database.connection import create_tables


async def main() -> None:
    await create_tables()

    scheduler = AsyncIOScheduler(timezone=UTC)
    scheduler.add_job(
        reload_users,
        trigger=CronTrigger(hour=cleanup.hour, minute=cleanup.minute),
        id="disable_expired_users",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()

    logger.info(f"Cleanup app started (daily at {cleanup.hour}:{cleanup.minute})")

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
