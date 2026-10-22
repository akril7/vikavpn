import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Coroutine


class AsyncRuntime:
    """Фоновый event loop для выполнения async-корутин из sync-кода.

    Гарантирует, что все корутины исполняются в одном и том же loop —
    это критично для async SQLAlchemy (asyncpg), которая привязывает
    соединения к loop.
    """

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="cli-async-runtime",
            daemon=True,
        )
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, Any], timeout: float | None = None) -> Any:
        """Синхронно выполняет корутину в фоновом loop."""
        future: Future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def shutdown(self) -> None:
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2)


runtime = AsyncRuntime()


def run(coro: Coroutine[Any, Any, Any], timeout: float | None = None) -> Any:
    """Удобная обёртка."""
    return runtime.run(coro, timeout=timeout)
