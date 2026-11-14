from aiohttp.web import Request, Response, json_response


async def handle_reload(request: Request) -> Response:
    """Запланировать reload через debounce."""
    request.app["reloader"].schedule()
    await request.app["expiry"].reschedule()
    return json_response({"ok": True})


async def handle_flush(request: Request) -> Response:
    """Немедленно применить конфиги."""
    try:
        await request.app["reloader"].flush()
        await request.app["expiry"].reschedule()
    except Exception:
        from loguru import logger
        logger.exception("Flush failed")
        return json_response({"ok": False}, status=500)
    return json_response({"ok": True})
