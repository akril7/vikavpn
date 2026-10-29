from aiohttp import web
from loguru import logger


async def handle_reload(request: web.Request) -> web.Response:
    """Запланировать reload через debounce."""
    request.app["reloader"].schedule()
    await request.app["expiry"].reschedule()
    return web.json_response({"ok": True})


async def handle_flush(request: web.Request) -> web.Response:
    """Немедленно применить конфиги."""
    try:
        await request.app["reloader"].flush()
        await request.app["expiry"].reschedule()
    except Exception:
        logger.exception("Flush failed")
        return web.json_response({"ok": False}, status=500)
    return web.json_response({"ok": True})
