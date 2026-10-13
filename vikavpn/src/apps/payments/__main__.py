from aiohttp import web

from src.settings import Settings

from .handler import handle_payment


def create_app(settings: Settings) -> web.Application:
    app = web.Application()
    app["yoomoney_secret"] = settings.yoomoney.secret
    app["reload_url"] = settings.reloader.url
    app["reload_timeout"] = settings.payments.reload_timeout

    app.router.add_post(settings.payments.payment_path, handle_payment)
    return app


def main(settings: Settings):
    web.run_app(
        create_app(settings),
        host=settings.payments.host,
        port=settings.payments.port,
    )


if __name__ == "__main__":
    main(Settings())
