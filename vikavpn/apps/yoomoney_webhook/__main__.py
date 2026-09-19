import hashlib
import hmac
from typing import Mapping
from urllib.parse import quote_plus

from aiohttp import web
from loguru import logger

from database.connection import Session
from config.yoomoney import YoomoneySettings
from services.payment.payment import confirm_payment


def verify_sign(data: Mapping[str, str], secret: str) -> bool:
    received = data.get("sign", "")
    if not received:
        return False

    filtered = {k: v for k, v in data.items() if k != "sign"}
    items = sorted(filtered.items())
    message = "&".join(f"{k}={quote_plus(str(v))}" for k, v in items)

    expected = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(received, expected)


async def handle_yoomoney(request: web.Request) -> web.Response:
    app = request.app

    data = dict(await request.post())
    logger.info(data)

    if not verify_sign(data, app["secret"]):
        logger.warning("YooMoney webhook: неверная подпись")
        return web.Response(status=403)

    label = data.get("label")

    async with Session() as session:
        await confirm_payment(session, label)

    return web.Response(status=201)


def create_app(secret: str, webhook_path: str) -> web.Application:
    app = web.Application()
    app["secret"] = secret
    app.router.add_post(webhook_path, handle_yoomoney)

    return app


if __name__ == "__main__":
    config = YoomoneySettings()
    web.run_app(create_app(config.secret, config.webhook_path), host=config.webhook_host, port=config.webhook_port)
