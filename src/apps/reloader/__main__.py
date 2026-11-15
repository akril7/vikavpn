from aiohttp.web import Application, run_app
from loguru import logger

from src.bootstrap.composition.builders import build_reloader_subsystem
from src.configuration import Settings
from src.infrastructure.network.socks import install_socks_proxy

from .api import handle_reload, handle_flush


def create_app(settings: Settings) -> Application:
    if settings.proxy.enabled:
        install_socks_proxy(settings.proxy.host, settings.proxy.port)

    registry, reloader, expiry = build_reloader_subsystem(settings)

    app = Application()
    app["reloader"] = reloader
    app["expiry"] = expiry

    app.router.add_post("/reload", handle_reload)
    app.router.add_post("/flush", handle_flush)

    async def _start(_: Application):
        reloader.start()
        await expiry.bootstrap()
        expiry.start()

    async def _stop(_: Application):
        await expiry.stop()
        await reloader.stop()

    app.on_startup.append(_start)
    app.on_shutdown.append(_stop)
    return app


def main(settings: Settings):
    app = create_app(settings)
    logger.info("app created")
    logger.info(f"run on {settings.reloader.host}:{settings.reloader.port}")
    run_app(
        app,
        host=settings.reloader.host,
        port=settings.reloader.port,
    )
    logger.info("app stopped")


if __name__ == "__main__":
    main(Settings())
