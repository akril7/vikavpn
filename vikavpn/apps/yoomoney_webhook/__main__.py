import hashlib
import hmac
from decimal import Decimal
from typing import Mapping
from urllib.parse import quote_plus

from aiohttp import web
from loguru import logger

from database.connection import Session
from services.core.reload import start_reload_worker
from settings import yoomoney
from services.payment import confirm_payment


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
        logger.warning("Неверная подпись")
        return web.Response(status=200)

    label = data.get("label")
    if not label:
        logger.warning("Пустой label")
        return web.Response(status=200)

    amount = data.get("withdraw_amount")
    if not amount:
        logger.warning("Пустой amount")
        return web.Response(status=200)

    async with Session() as session:
        await confirm_payment(session, label, Decimal(amount))

    return web.Response(status=200)


async def on_startup(_: web.Application):
    start_reload_worker()


def create_app(secret: str, webhook_path: str) -> web.Application:
    app = web.Application()
    app["secret"] = secret
    app.on_startup.append(on_startup)
    app.router.add_post(webhook_path, handle_yoomoney)
    return app


if __name__ == "__main__":
    web.run_app(
        create_app(yoomoney.secret, yoomoney.webhook_path),
        host=yoomoney.webhook_host,
        port=yoomoney.webhook_port,
    )
