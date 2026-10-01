import re

from uuid import UUID

from src.db.models import User, Payment

TG_PROXY_RE = re.compile(r"secret=ee([0-9a-f]{32})", re.IGNORECASE)
SUB_RE = re.compile(r"https?://[^/]+/sub/([0-9a-f]{32})", re.IGNORECASE)


def parse_uuid_from_link(text: str) -> UUID | None:
    for pattern in (TG_PROXY_RE, SUB_RE):
        match = pattern.search(text)
        if match is not None:
            return UUID(hex=match.group(1))
    return None


def build_telegram_proxy_url(user: User, sni: str, domain: str, port: int) -> str:
    uuid = user.uuid.hex
    sni = sni.encode().hex()

    return f"tg://proxy?server={domain}&port={port}&secret=ee{uuid}{sni}"


def build_bot_auth_url(bot_username: str, user: User) -> str:
    return f"https://t.me/{bot_username}?start={user.uuid.hex}"


def build_payment_url(payment: Payment, receiver: str) -> str:
    return (
        "https://yoomoney.ru/quickpay/confirm.xml"
        f"?receiver={receiver}"
        "&quickpay-form=button"
        f"&sum={payment.amount:.2f}"
        f"&label={payment.label}"
    )
