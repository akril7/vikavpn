from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.date import DateTrigger
from loguru import logger

from src.core.reloader import Reloader
from src.db.connection import Session
from src.db.repo import UserRepository


JOB_ID = "disable_expired_users"
EXPIRY_GRACE = timedelta(seconds=5)
FALLBACK_INTERVAL = timedelta(hours=1)
MISFIRE_GRACE_SECONDS = 60


class Disabler:
    """Планирует reload конфигов в момент истечения ближайшей подписки"""

    def __init__(self, reloader: Reloader) -> None:
        self._reloader = reloader
        self._scheduler = AsyncIOScheduler(timezone=UTC)

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Disabler scheduler started")

    async def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Disabler scheduler stopped")

    async def bootstrap(self) -> None:
        """Синхронизация на старте: применить активных и запланировать следующий тик."""
        await self._reloader.flush()
        await self.reschedule()

    async def reschedule(self) -> None:
        """Перепланировать ближайший tick по данным из БД."""
        try:
            next_at = await self._get_next_expire_at()
        except Exception:
            logger.exception("Failed to read next expire, fallback")
            next_at = None

        now = datetime.now(UTC)

        if next_at is None:
            run_at = now + FALLBACK_INTERVAL
            logger.info("No active subscriptions, next check at {}", run_at)
        else:
            run_at = max(next_at + EXPIRY_GRACE, now)
            logger.info("Next expiry at {}, run at {}", next_at, run_at)

        self._add_job(
            DateTrigger(run_date=run_at)
        )

    async def _tick(self) -> None:
        try:
            logger.info("Disabler tick: applying active users")
            await self._reloader.flush()
            await self.reschedule()
        except Exception:
            logger.exception(
                "Disabler tick failed, retrying in {}", FALLBACK_INTERVAL
            )
            self._add_job(
                DateTrigger(run_date=datetime.now(UTC) + FALLBACK_INTERVAL)
            )

    def _add_job(self, trigger: BaseTrigger):
        self._scheduler.add_job(
            self._tick,
            trigger=trigger,
            id=JOB_ID,
            replace_existing=True,
            misfire_grace_time=MISFIRE_GRACE_SECONDS,
            max_instances=1,
            coalesce=True,
        )

    @staticmethod
    async def _get_next_expire_at() -> datetime | None:
        async with Session() as session:
            repo = UserRepository(session)
            return await repo.get_next_expire_at()
