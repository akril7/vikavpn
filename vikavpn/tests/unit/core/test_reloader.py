import asyncio

from src.core.reloader import Reloader


async def test_flush_calls_apply():
    calls = []

    async def apply():
        calls.append(1)

    r = Reloader(apply, debounce=1.0, max_delay=5.0)
    r.start()
    try:
        await r.flush()
    finally:
        await r.stop()

    assert calls == [1]


async def test_schedule_triggers_apply_after_debounce():
    calls = []

    async def apply():
        calls.append(1)

    r = Reloader(apply, debounce=0.1, max_delay=1.0)
    r.start()
    try:
        r.schedule()
        await asyncio.sleep(0.3)
    finally:
        await r.stop()

    assert len(calls) >= 1


async def test_debounce_coalesces_multiple_schedules():
    calls = []

    async def apply():
        calls.append(1)

    r = Reloader(apply, debounce=0.2, max_delay=2.0)
    r.start()
    try:
        for _ in range(5):
            r.schedule()
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.5)
    finally:
        await r.stop()

    # Все 5 schedule должны схлопнуться в 1 apply
    assert len(calls) == 1


async def test_max_delay_forces_apply():
    calls = []

    async def apply():
        calls.append(1)

    r = Reloader(apply, debounce=10.0, max_delay=0.2)
    r.start()
    try:
        r.schedule()
        # постоянно "сбрасываем" debounce, но max_delay должен заставить apply
        for _ in range(10):
            await asyncio.sleep(0.05)
            r.schedule()
        await asyncio.sleep(0.5)
    finally:
        await r.stop()

    assert len(calls) >= 1


async def test_stop_terminates_worker():
    calls = []

    async def apply():
        calls.append(1)

    r = Reloader(apply, debounce=10.0, max_delay=20.0)
    r.start()

    await r.stop()

    # После stop — новая задача не должна запускаться
    r.schedule()
    await asyncio.sleep(0.1)
    assert calls == []


async def test_apply_exception_does_not_crash_worker():
    calls = []

    async def apply():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom")

    r = Reloader(apply, debounce=0.1, max_delay=1.0)
    r.start()
    try:
        r.schedule()
        await asyncio.sleep(0.3)
        r.schedule()
        await asyncio.sleep(0.3)
    finally:
        await r.stop()

    assert len(calls) >= 2
