import hashlib
import hmac
from decimal import Decimal
from typing import Mapping
from urllib.parse import quote_plus

from aiohttp import web
from loguru import logger

from src.core.lifecycle.notify import notify_reload
from src.core.payment.lifecycle import confirm_payment
from src.db.connection import Session
from src.db.repo import UserRepository, PaymentRepository, PaymentUserRepository


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


async def handle_payment(request: web.Request) -> web.Response:
    app = request.app
    data = dict(await request.post())

    label = data.get("label")
    amount = data.get("withdraw_amount")

    if not verify_sign(data, app["yoomoney_secret"]):
        logger.warning("Invalid yoomoney signature")
        return web.Response(status=200)

    if not label:
        logger.warning("Missing label in payment notification")
        return web.Response(status=200)

    if not amount:
        logger.warning("Missing amount in payment notification")
        return web.Response(status=200)

    async with Session() as session:
        payment = await confirm_payment(
            UserRepository(session),
            PaymentRepository(session),
            PaymentUserRepository(session),
            label,
            Decimal(amount),
        )
        await session.commit()

    if payment:
        # Платёж подтверждён — просим reload перепланировать tick по expiry.
        # Если reload недоступен — не страшно: bootstrap подхватит на следующем старте.
        await notify_reload(
            app["reload_url"],
            timeout=app["reload_timeout"],
        )

        logger.debug(payment.label)

    return web.Response(status=200)
