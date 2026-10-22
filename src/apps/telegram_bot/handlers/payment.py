from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.core.payment.lifecycle import get_paid_payment
from src.settings import Settings
from src.db.connection import Session
from src.db.repo import UserRepository, options, PaymentRepository, PaymentUserRepository
from src.db.enums import Tariff

from src.core.users.flow.renew import (
    RenewMode,
    RenewError,
    PayerNotFoundError,
    TargetNotFoundError,
    create_payment_for_renew
)

from ..keyboards import back_menu, payment_menu
from src.texts.render import (
    render_payment_created,
    render_payment_not_paid,
    render_payment_paid,
    render_auth_user_not_found,
)

router = Router()


async def start_payment_for_renew(
    call: CallbackQuery,
    state: FSMContext,
    settings: Settings,
):
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
        try:
            payment, url = await create_payment_for_renew(
                user_repo=UserRepository(session),
                payment_repo=PaymentRepository(session),
                link_repo=PaymentUserRepository(session),
                telegram_id=call.from_user.id,
                mode=mode,
                tariff=tariff,
                days=days,
                receiver=settings.yoomoney.receiver,
                fee_percent=settings.yoomoney.fee_percent,
                target_id=target_id,
            )
        except PayerNotFoundError:
            await call.answer(render_auth_user_not_found(), show_alert=True)
            return
        except TargetNotFoundError as exc:
            await call.answer(exc.message, show_alert=True)
            return
        except RenewError as exc:
            await call.answer(exc.message, show_alert=True)
            return
        except ValueError:
            await call.answer()
            return

        await session.commit()

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
