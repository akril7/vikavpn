import asyncio
from datetime import UTC, datetime, timedelta
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger

from src.settings import Settings
from src.db.connection import create_tables, Session
from src.db.repo import UserRepository
from src.core.reload import Reloader
from src.infrastructure.manager.configure import build_reloader
from src.infrastructure.manager.registry import Registry


JOB_ID = "disable_expired_users"
EXPIRY_GRACE = timedelta(seconds=5)
FALLBACK_INTERVAL = timedelta(hours=1)


async def _get_next_expire_at() -> datetime | None:
    async with Session() as session:
        repo = UserRepository(session)
        return await repo.get_next_expire_at()


async def _schedule_next(
    scheduler: AsyncIOScheduler,
    reloader: Reloader,
) -> None:
    old = scheduler.get_job(JOB_ID)
    if old is not None:
        old.remove()

    next_at = await _get_next_expire_at()
    now = datetime.now(UTC)

    if next_at is None:
        run_at = now + FALLBACK_INTERVAL
        logger.info("No active subscriptions, next check at {}", run_at)
    else:
        run_at = next_at + EXPIRY_GRACE
        logger.info("Next expiry at {}, run at {}", next_at, run_at)

    scheduler.add_job(
        partial(_tick, scheduler=scheduler, reloader=reloader),
        trigger=DateTrigger(run_date=run_at),
        id=JOB_ID,
        replace_existing=True,
        misfire_grace_time=3600,
        max_instances=1,
        coalesce=True,
    )


async def _tick(scheduler: AsyncIOScheduler, reloader: Reloader) -> None:
    logger.info("Disabler tick: scheduling reload")
    reloader.schedule()
    await _schedule_next(scheduler, reloader)


async def main(settings: Settings) -> None:
    await create_tables()

    registry = Registry(settings)
    reloader = build_reloader(registry)
    reloader.start()

    scheduler = AsyncIOScheduler(timezone=UTC)
    scheduler.start()

    await _schedule_next(scheduler, reloader)

    logger.info("Disabler app started")

    try:
        await asyncio.Event().wait()
    finally:
        if scheduler.running:
            scheduler.shutdown()
        await reloader.stop()


if __name__ == "__main__":
    asyncio.run(main(Settings()))
