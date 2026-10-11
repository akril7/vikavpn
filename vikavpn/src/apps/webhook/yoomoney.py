import hashlib
import hmac
from decimal import Decimal
from typing import Mapping
from urllib.parse import quote_plus

from aiohttp import web
from loguru import logger

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
        logger.warning("Неверная подпись")

    elif not label:
        logger.warning("Пустой label")

    elif not amount:
        logger.warning("Пустой amount")

    else:
        async with Session() as session:
            user_repo = UserRepository(session)
            payment_repo = PaymentRepository(session)
            link_repo = PaymentUserRepository(session)
            payment = await confirm_payment(user_repo, payment_repo, link_repo
                                            , label, Decimal(amount))

            await session.commit()

        if payment:
            await app["disabler"].reschedule()
            app["reloader"].schedule()

    return web.Response(status=200)
