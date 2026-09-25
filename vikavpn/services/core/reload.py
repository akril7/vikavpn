import asyncio
import time
from loguru import logger

from services.core.commands import reload_users

DEBOUNCE_SECONDS = 5.0     # пауза после последнего изменения
MAX_DELAY_SECONDS = 30.0   # максимум ожидания даже при непрерывных изменениях

_dirty = asyncio.Event()
_first_change_at: float | None = None
_worker_task: asyncio.Task | None = None


async def _worker() -> None:
    global _first_change_at

    while True:
        await _dirty.wait()

        if _first_change_at is None:
            _first_change_at = time.monotonic()

        elapsed = time.monotonic() - _first_change_at
        wait = max(0.0, min(DEBOUNCE_SECONDS, MAX_DELAY_SECONDS - elapsed))
        if wait > 0:
            await asyncio.sleep(wait)

        _dirty.clear()
        _first_change_at = None

        try:
            logger.info("Reloading users configuration...")
            await reload_users()
            logger.info("Reload complete")
        except Exception:
            logger.exception("reload_users failed")


def start_reload_worker() -> None:
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker())
        logger.info("Reload worker started")


def schedule_reload() -> None:
    _dirty.set()
