from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.connection import Session
from database.models import Messenger
from services.bot.registration import register_user

from ..keyboards import main_menu, platform_menu
from ..render import render_platform_question, render_register_success
from ..states import Register

router = Router()


@router.callback_query(F.data == "auth:register")
async def cb_register(call: CallbackQuery, state: FSMContext):
    await state.set_state(Register.platform)
    await call.message.edit_text(
        render_platform_question(),
        reply_markup=platform_menu(),
    )
    await call.answer()


@router.callback_query(Register.platform, F.data.startswith("register:ios:"))
async def cb_register_platform(call: CallbackQuery, state: FSMContext):
    ios = call.data.rsplit(":", 1)[-1] == "1"

    await state.clear()
    await call.message.edit_text("Регистрируем вас...")

    async with Session() as session:
        user = await register_user(
            session,
            Messenger.TELEGRAM,
            call.from_user.id,
            ios_user=ios,
        )

    await call.message.edit_text(
        render_register_success(user.name, user.password),
    )
    await call.message.answer("Главное меню", reply_markup=main_menu())
    await call.answer()
