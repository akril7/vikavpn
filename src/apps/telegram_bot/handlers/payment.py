from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.application.payment import get_paid_payment, create_payment
from src.application.urls import build_payment_url
from src.configuration import Settings
from src.infrastructure.persistence.connection import Session
from src.infrastructure.persistence.repo import UserRepository, options, PaymentRepository, PaymentUserRepository
from src.domain.enums import Tariff

from ..keyboards import back_menu, payment_menu
from ..texts.render import render_auth_user_not_found, render_payment_created, render_payment_not_paid, \
    render_payment_paid

router = Router()


async def start_payment_for_renew(
    call: CallbackQuery,
    state: FSMContext,
    settings: Settings,
):
    data = await state.get_data()
    try:
        tariff = Tariff(data["tariff"])
        days = data["days"]
    except KeyError:
        await call.answer()
        return

    async with Session() as session:
        user_repo = UserRepository(session)
        payer = await user_repo.get_by_telegram_id(call.from_user.id)
        if not payer:
            await call.answer(render_auth_user_not_found(), show_alert=True)
            return

        try:
            payment = await create_payment(
                payment_repo=PaymentRepository(session),
                link_repo=PaymentUserRepository(session),
                payer=payer,
                targets=[payer],
                tariff=tariff,
                days=days,
                fee_percent=settings.yoomoney.fee_percent,
            )
        except ValueError:
            await call.answer()
            return

        await session.commit()

    await state.clear()

    url = build_payment_url(settings, payment)
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

        payer = await user_repo.get_with(
            payment.payer_id,
            options=options.messenger_options(),
        )
        if not payer:
            await call.answer(render_auth_user_not_found(), show_alert=True)
            return

        if payer.telegram_id != call.from_user.id:
            await call.answer()
            return

        expires_at = payer.sub_expires_at

    await call.message.edit_text(
        render_payment_paid(expires_at),
        reply_markup=back_menu("menu:main"),
    )

    await call.answer()
