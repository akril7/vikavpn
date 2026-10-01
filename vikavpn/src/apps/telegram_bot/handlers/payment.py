from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.settings import Settings
from src.db.connection import Session
from src.db.repo import UserRepository
from src.db.enums import Messenger, Tariff
from src.db.models import User
from src.apps.telegram_bot.service.menu import RenewMode
from src.apps.telegram_bot.service.payment import (
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


async def create_payment_for_renew(call: CallbackQuery, state: FSMContext, settings: Settings):
    data = await state.get_data()
    mode = RenewMode(data["mode"])
    tariff = Tariff(data["tariff"])
    days = data["days"]

    async with Session() as session:
        repo = UserRepository(session)

        payer = await repo.get_by_messenger(Messenger.TELEGRAM, call.from_user.id)
        if payer is None:
            await call.answer("Пользователь не найден", show_alert=True)
            return

        payer_full = await repo.get_with_managed_users(payer.id)

        if mode == RenewMode.SELF:
            targets = [payer_full]
        elif mode == RenewMode.SELF_AND_MANAGED:
            targets = [payer_full, *(link.managed for link in payer_full.managed_links)]
        else:
            target_id = data["target_id"]
            targets = [link.managed for link in payer_full.managed_links if link.managed.id == target_id]
            if not targets:
                await call.answer("Пользователь не найден", show_alert=True)
                return

        payment, url = await start_payment(
            session,
            payer=payer_full,
            targets=targets,
            tariff=tariff,
            days=days,
            receiver=settings.yoomoney.receiver,
            fee_percent=settings.yoomoney.fee_percent
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

    await call.message.edit_text(
        render_payment_paid(payer.sub_expires_at),
        reply_markup=back_menu("menu:main"),
    )
    await call.answer()
