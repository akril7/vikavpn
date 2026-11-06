from src.configuration import Settings
from src.configuration.app import LINK_DOMAIN
from src.domain.models import User, Payment
from src.domain.urls.link import (
    build_telegram_proxy_url as _build_telegram_proxy_url,
    build_bot_auth_url as _build_bot_auth_url,
    build_payment_url as _build_payment_url
)


def build_telegram_proxy_url(settings: Settings, user: User) -> str:
    domain = LINK_DOMAIN or settings.tls.domain
    return _build_telegram_proxy_url(user=user, domain=domain)


def build_bot_auth_url(settings: Settings, user: User) -> str:
    bot_username = settings.telegram_bot.username
    return _build_bot_auth_url(bot_username=bot_username, user=user)


def build_payment_url(settings: Settings, payment: Payment) -> str:
    return _build_payment_url(payment=payment, receiver=settings.yoomoney.receiver)
