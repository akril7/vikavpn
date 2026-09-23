# apps/telegram_bot/render.py
from datetime import datetime

from services.bot import texts
from services.bot.profile import ProfileView


def render_start_not_authorized() -> str:
    return texts.START_NOT_AUTHORIZED


def render_auth_ask_link() -> str:
    return texts.AUTH_ASK_LINK


def render_auth_success() -> str:
    return texts.AUTH_SUCCESS


def render_auth_user_not_found() -> str:
    return texts.AUTH_USER_NOT_FOUND


def render_auth_already_bound() -> str:
    return texts.AUTH_ALREADY_BOUND


def render_platform_question() -> str:
    return texts.REGISTER_CHOOSE_PLATFORM


def render_register_success(name: str, password: str) -> str:
    return texts.REGISTER_SUCCESS.format(name=name, password=password)


def render_profile(profile: ProfileView) -> str:
    status = (
        texts.STATUS_ACTIVE.format(days=profile.days_left)
        if profile.is_active
        else texts.STATUS_EXPIRED
    )
    text = (
        f"<b>{texts.PROFILE_HEADER}</b>\n\n"
        + texts.PROFILE_BODY.format(
            expires_at=profile.expires_at.strftime("%d.%m.%Y"),
            status=status,
        )
    )
    if profile.managed_names:
        text += "\n\n👥 <b>Можно оплатить за:</b>\n" + ", ".join(
            profile.managed_names
        )
    return text


def render_renew_choose_mode() -> str:
    return texts.RENEW_CHOOSE_MODE


def render_renew_choose_tariff() -> str:
    return texts.RENEW_CHOOSE_TARIFF


def render_renew_choose_days() -> str:
    return texts.RENEW_CHOOSE_DAYS


def render_renew_choose_target() -> str:
    return texts.RENEW_CHOOSE_TARGET


def render_payment_created(amount: int) -> str:
    return f"💳 Платёж создан на сумму <b>{amount} ₽</b>\n\n" + (
        "Оплатите по ссылке ниже. После оплаты нажмите "
        "«Проверить оплату»."
    )


def render_payment_not_found() -> str:
    return texts.PAYMENT_NOT_FOUND


def render_payment_not_paid() -> str:
    return texts.PAYMENT_NOT_PAID


def render_payment_paid(expires_at: datetime) -> str:
    return texts.PAYMENT_PAID.format(
        expires_at=expires_at.strftime("%d.%m.%Y")
    )


def render_help(video_url: str, admin_username: str) -> str:
    return texts.HELP_TEXT.format(video_url=video_url, admin=admin_username)
