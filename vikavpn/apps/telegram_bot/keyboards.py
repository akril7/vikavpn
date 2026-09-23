from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton

from services.bot import texts
from services.bot.menu import RenewMode
from services.payment.plans import Plan


def auth_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_AUTH_BY_LINK, callback_data="auth:link")],
        [InlineKeyboardButton(text=texts.BTN_REGISTER, callback_data="auth:register")],
    ])


def platform_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_PLATFORM_IOS, callback_data="register:ios:1")],
        [InlineKeyboardButton(text=texts.BTN_PLATFORM_OTHER, callback_data="register:ios:0")],
    ])


def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=texts.BTN_PROFILE, callback_data="menu:profile")],
        [InlineKeyboardButton(text=texts.BTN_RENEW, callback_data="menu:renew")],
        [InlineKeyboardButton(text=texts.BTN_HELP, callback_data="menu:help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def profile_menu(telegram_link: str | None, clash_link: str | None) -> InlineKeyboardMarkup:
    rows = []
    if clash_link:
        rows.append([InlineKeyboardButton(text=texts.BTN_COPY_CLASH_LINK, copy_text=CopyTextButton(text=clash_link))])

    if telegram_link:
        rows.append([InlineKeyboardButton(text=texts.BTN_CONNECT_PROXY, url=telegram_link)])

    rows.append([InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:main")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_menu(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_BACK, callback_data=callback)],
    ])


def renew_menu(has_managed: bool) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=texts.BTN_RENEW_SELF,
            callback_data=f"renew:{RenewMode.SELF}",
        )],
    ]
    if has_managed:
        rows.append([InlineKeyboardButton(
            text=texts.BTN_RENEW_SELF_AND_MANAGED,
            callback_data=f"renew:{RenewMode.SELF_AND_MANAGED}",
        )])
        rows.append([InlineKeyboardButton(
            text=texts.BTN_RENEW_OTHER,
            callback_data=f"renew:{RenewMode.OTHER}",
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tariff_menu(proxy_price: int, full_price: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.BTN_TARIFF_PROXY.format(price=proxy_price),
            callback_data="tariff:proxy",
        )],
        [InlineKeyboardButton(
            text=texts.BTN_TARIFF_FULL.format(price=full_price),
            callback_data="tariff:full",
        )],
        [InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:renew")],
    ])


def days_menu(plans: list[Plan]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=texts.BTN_DAYS.format(days=p.days, price=p.price),
            callback_data=f"days:{p.days}",
        )]
        for p in plans
    ]
    rows.append([InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:renew")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def targets_menu(targets: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"target:{uid}")]
        for uid, name in targets
    ]
    rows.append([InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:renew")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_menu(pay_url: str, label: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_PAY, url=pay_url)],
        [InlineKeyboardButton(
            text=texts.BTN_CHECK_PAYMENT,
            callback_data=f"check:{label}",
        )],
        [InlineKeyboardButton(text=texts.BTN_BACK, callback_data="menu:main")],
    ])
