from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import yoomoney
from database.connection import Session
from database.crud import get_user_by_messenger, get_user_with_managed
from database.models import Messenger, Tariff, User
from services.bot.menu import RenewMode
from services.bot.payment import (
    PaymentCheckResult,
    check_payment,
    start_payment,
)

from ..keyboards import back_menu, payment_menu
from ..render import (
    render_payment_created,
    render_payment_not_found,
    render_payment_not_paid,
    render_payment_paid,
)

router = Router()


async def create_payment_for_renew(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mode = RenewMode(data["mode"])
    tariff = Tariff(data["tariff"])
    days = data["days"]

    async with Session() as session:
        payer = await get_user_by_messenger(
            session, Messenger.TELEGRAM, call.from_user.id
        )
        if payer is None:
            await call.answer("Пользователь не найден", show_alert=True)
            return

        payer_full = await get_user_with_managed(session, payer.id)

        if mode == RenewMode.SELF:
            targets = [payer_full]
        elif mode == RenewMode.SELF_AND_MANAGED:
            targets = [payer_full, *payer_full.managed_users]
        else:
            target_id = data["target_id"]
            targets = [
                u for u in payer_full.managed_users if u.id == target_id
            ]
            if not targets:
                await call.answer("Пользователь не найден", show_alert=True)
                return

        payment, url = await start_payment(
            session,
            payer=payer_full,
            targets=targets,
            tariff=tariff,
            days=days,
            receiver=yoomoney.receiver,
        )

    await state.clear()
    await call.message.edit_text(
        render_payment_created(payment.amount),
        reply_markup=payment_menu(pay_url=url, label=payment.label),
    )
    await call.answer()


@router.callback_query(F.data.startswith("check:"))
async def cb_check_payment(call: CallbackQuery):
    label = call.data.split(":", 1)[1]

    async with Session() as session:
        result, payment = await check_payment(session, label)

        if result == PaymentCheckResult.NOT_FOUND:
            await call.answer(render_payment_not_found(), show_alert=True)
            return
        if result == PaymentCheckResult.NOT_PAID:
            await call.answer(render_payment_not_paid(), show_alert=True)
            return

        payer = await session.get(User, payment.payer_id)
        expires_at = payer.sub_expires_at if payer else None

    await call.message.edit_text(
        render_payment_paid(expires_at),
        reply_markup=back_menu("menu:main"),
    )
    await call.answer()
