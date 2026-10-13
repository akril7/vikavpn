import aiohttp
from loguru import logger


async def notify_reload(reload_url: str, timeout: float = 5.0) -> None:
    """Попросить reload-приложение применить конфиги (debounced)."""
    await _post(f"{reload_url}/reload", timeout, "reload")


async def notify_flush(reload_url: str, timeout: float = 5.0) -> None:
    """Попросить reload-приложение немедленно применить конфиги."""
    await _post(f"{reload_url}/flush", timeout, "flush")


async def _post(url: str, timeout: float, name: str) -> None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                if resp.status != 200:
                    logger.warning("{} returned {} from {}", name, resp.status, url)
    except Exception:
        logger.exception("Failed to notify {} at {}", name, url)
