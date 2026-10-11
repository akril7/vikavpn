from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.core.payment.lifecycle import create_payment, get_paid_payment
from src.settings import Settings
from src.db.connection import Session
from src.db.repo import UserRepository, options, PaymentRepository, PaymentUserRepository
from src.db.enums import Tariff

from src.core.users.flow.renew import RenewMode

from ..keyboards import back_menu, payment_menu
from src.texts.render import (
    render_payment_created,
    render_payment_not_paid,
    render_payment_paid, render_auth_user_not_found
)

router = Router()


async def create_payment_for_renew(call: CallbackQuery, state: FSMContext, settings: Settings):
    data = await state.get_data()
    try:
        mode = RenewMode(data["mode"])
        tariff = Tariff(data["tariff"])
        days = data["days"]
        target_id = data.get("target_id")
    except KeyError:
        await call.answer()
        return

    async with Session() as session:
        repo = UserRepository(session)
        payer = await repo.get_by_telegram_id(call.from_user.id, options=options.managed_options())
        if not payer:
            await call.answer(render_auth_user_not_found(), show_alert=True)
            return

        if mode == RenewMode.SELF:
            targets = [payer]
        elif mode == RenewMode.SELF_AND_MANAGED:
            targets = [payer, *(link.managed for link in payer.managed_links if link.managed)]
        elif mode == RenewMode.OTHER:
            targets = [link.managed for link in payer.managed_links if link.managed and link.managed.id == target_id]
            if not targets:
                await call.answer("Пользователь не найден", show_alert=True)
                return
        else:
            raise RuntimeError("Not implemented renew mode")

        payment_repo = PaymentRepository(session)
        link_repo = PaymentUserRepository(session)

        payment, url = await create_payment(
            payment_repo=payment_repo,
            link_repo=link_repo,
            payer=payer,
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
        user_repo = UserRepository(session)
        payment_repo = PaymentRepository(session)

        payment = await get_paid_payment(payment_repo, label)
        if payment is None:
            await call.answer(render_payment_not_paid(), show_alert=True)
            return

        payer = await user_repo.get_with(payment.payer_id, options=options.messenger_options())
        if not payer:
            await call.answer(render_auth_user_not_found(), show_alert=True)
            return

        if payer.telegram_id != call.from_user.id:
            return

        expires_at = payer.sub_expires_at

    await call.message.edit_text(
        render_payment_paid(expires_at),
        reply_markup=back_menu("menu:main"),
    )

    await call.answer()
