import asyncio
import time
from collections.abc import Awaitable, Callable
from loguru import logger


class Reloader:
    """Debounced async reloader.

    Гарантирует:
    - не более одного применения за раз (lock);
    - debounce + max_delay;
    - корректное завершение при stop();
    - ошибки логируются, но не убивают worker.
    """

    def __init__(
        self,
        apply: Callable[[], Awaitable[None]],
        debounce: float = 3.0,
        max_delay: float = 30.0,
    ) -> None:
        self._apply = apply
        self._debounce = debounce
        self._max_delay = max_delay

        self._dirty = asyncio.Event()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self._stopping = False

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stopping = False
            self._task = asyncio.create_task(self._worker())
            logger.info("Reloader started")

    def schedule(self) -> None:
        self._dirty.set()

    async def stop(self) -> None:
        self._stopping = True
        self._dirty.set()  # разбудить worker, если спит

        if self._task and not self._task.done():
            try:
                await asyncio.wait_for(self._task, timeout=self._max_delay + 5)
            except asyncio.TimeoutError:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            except asyncio.CancelledError:
                pass

        self._task = None
        logger.info("Reloader stopped")

    async def _worker(self) -> None:
        while not self._stopping:
            await self._dirty.wait()
            self._dirty.clear()

            first_change_at = time.monotonic()

            # Ждём debounce, но не дольше max_delay
            while True:
                elapsed = time.monotonic() - first_change_at
                remaining_max = self._max_delay - elapsed
                if remaining_max <= 0:
                    break

                wait = min(self._debounce, remaining_max)
                try:
                    await asyncio.wait_for(self._dirty.wait(), timeout=wait)
                    self._dirty.clear()
                    # пришло новое событие — ждём ещё debounce
                except asyncio.TimeoutError:
                    break

            if self._stopping:
                break

            async with self._lock:
                logger.info("Applying configuration...")
                try:
                    await self._apply()
                    logger.info("Configuration applied")
                except Exception:
                    logger.exception("Configuration apply failed")
