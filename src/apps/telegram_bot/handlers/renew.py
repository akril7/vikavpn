from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.db.enums import Tariff
from src.texts import texts
from src.core.users.flow.renew import RenewMode
from src.core.payment.plans import get_plans
from src.db.repo import options
from src.settings import Settings

from ..deps import managed_targets, get_user_or_alert
from ..keyboards import days_menu, renew_menu, targets_menu, tariff_menu
from src.texts.render import (
    render_renew_choose_days,
    render_renew_choose_tariff,
    render_renew_choose_target, render_renew_choose_mode,
)
from ..states import Renew

from .payment import start_payment_for_renew

router = Router()


@router.callback_query(F.data == "menu:renew")
async def cb_renew(call: CallbackQuery, state: FSMContext):
    user = await get_user_or_alert(call, options=options.managed_options())
    if user is None:
        return

    await state.clear()
    await call.message.edit_text(
        render_renew_choose_mode(),
        reply_markup=renew_menu(has_managed=bool(user.managed_links)),
    )
    await call.answer()


@router.callback_query(F.data.startswith("renew:"))
async def cb_renew_mode(call: CallbackQuery, state: FSMContext):
    try:
        mode = RenewMode(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer()
        return

    await state.update_data(mode=mode.value)
    await state.set_state(Renew.tariff)

    proxy_plans = get_plans(Tariff.PROXY)
    full_plans = get_plans(Tariff.FULL)
    await call.message.edit_text(
        render_renew_choose_tariff(),
        reply_markup=tariff_menu(
            proxy_price=proxy_plans[0].price,
            full_price=full_plans[0].price,
        ),
    )

    await call.answer()


@router.callback_query(Renew.tariff, F.data.startswith("tariff:"))
async def cb_renew_tariff(call: CallbackQuery, state: FSMContext):
    try:
        tariff = Tariff(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer()
        return

    if tariff == Tariff.PROXY:
        user = await get_user_or_alert(call)
        if user is None:
            return
        elif user.vpn_user and user.is_active:
            await call.answer(texts.RENEW_PROXY_BLOCKED_BY_VPN, show_alert=True)
            return

    await state.update_data(tariff=tariff.value)
    await state.set_state(Renew.days)

    await call.message.edit_text(
        render_renew_choose_days(),
        reply_markup=days_menu(get_plans(tariff)),
    )
    await call.answer()


@router.callback_query(Renew.days, F.data.startswith("days:"))
async def cb_renew_days(call: CallbackQuery, state: FSMContext, settings: Settings):
    try:
        days = int(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer()
        return

    await state.update_data(days=days)

    data = await state.get_data()
    try:
        mode = RenewMode(data["mode"])
    except (ValueError, KeyError):
        await call.answer()
        return

    if mode == RenewMode.OTHER:
        user = await get_user_or_alert(call, options=options.managed_options())
        if not user:
            return

        await state.set_state(Renew.target)
        await call.message.edit_text(
            render_renew_choose_target(),
            reply_markup=targets_menu(managed_targets(user)),
        )
        await call.answer()
        return

    await start_payment_for_renew(call, state, settings)


@router.callback_query(Renew.target, F.data.startswith("target:"))
async def cb_renew_target(call: CallbackQuery, state: FSMContext, settings: Settings):
    try:
        target_id = int(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer()
        return

    await state.update_data(target_id=target_id)

    await start_payment_for_renew(call, state, settings)
