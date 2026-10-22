from aiohttp import web

from src.settings import Settings

from .handler import handle_auth


def create_app(settings: Settings) -> web.Application:
    app = web.Application()
    app.router.add_post(settings.hysteria.auth_path, handle_auth)
    return app


def main(settings: Settings):
    web.run_app(
        create_app(settings),
        host=settings.hysteria.auth_host,
        port=settings.hysteria.auth_port,
    )


if __name__ == "__main__":
    main(Settings())
