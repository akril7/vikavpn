from urllib.parse import urljoin

from aiohttp import web

from src.apps.webhook.disabler import Disabler
from src.infrastructure.manager.configure import build_reloader
from src.infrastructure.manager.registry import Registry
from src.settings import Settings

from . import yoomoney, hysteria


def create_app(settings: Settings) -> web.Application:
    registry = Registry(settings)
    reloader = build_reloader(registry)
    disabler = Disabler(reloader)

    app = web.Application()
    app["yoomoney_secret"] = settings.yoomoney.secret
    app["reloader"] = reloader
    app["disabler"] = disabler

    async def _start_scheduler(_: web.Application):
        reloader.start()
        await disabler.bootstrap()
        disabler.start()

    async def _stop_scheduler(_: web.Application):
        await disabler.stop()
        await reloader.stop()

    app.on_startup.append(_start_scheduler)
    app.on_shutdown.append(_stop_scheduler)

    app.router.add_post(
        urljoin(settings.webhook.urlpath,
                settings.webhook.yoomoney_payment_urlpath),
        yoomoney.handle_payment)
    app.router.add_post(
        urljoin(settings.webhook.urlpath,
                settings.webhook.hysteria_auth_urlpath),
        hysteria.handle_auth)

    return app


def main(settings: Settings):
    web.run_app(
        create_app(settings),
        host=settings.webhook.host,
        port=settings.webhook.port,
    )


if __name__ == "__main__":
    main(Settings())
