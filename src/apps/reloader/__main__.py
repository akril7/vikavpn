from aiohttp import web

from src.core.lifecycle.expiryscheduler import ExpiryScheduler
from src.infrastructure.manager.configure import build_reloader
from src.infrastructure.manager.registry import Registry
from src.settings import Settings

from .api import handle_reload, handle_flush


def create_app(settings: Settings) -> web.Application:
    registry = Registry(settings)
    reloader = build_reloader(
        registry,
        debounce=settings.reloader.debounce,
        max_delay=settings.reloader.max_delay,
    )
    expiry = ExpiryScheduler(reloader)

    app = web.Application()
    app["reloader"] = reloader
    app["expiry"] = expiry

    app.router.add_post("/reload", handle_reload)
    app.router.add_post("/flush", handle_flush)

    async def _start(_: web.Application):
        reloader.start()
        await expiry.bootstrap()
        expiry.start()

    async def _stop(_: web.Application):
        await expiry.stop()
        await reloader.stop()

    app.on_startup.append(_start)
    app.on_shutdown.append(_stop)
    return app


def main(settings: Settings):
    web.run_app(
        create_app(settings),
        host=settings.reloader.host,
        port=settings.reloader.port,
    )


if __name__ == "__main__":
    main(Settings())
