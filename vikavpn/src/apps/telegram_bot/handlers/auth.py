from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.db.connection import Session
from src.db.enums import Messenger

from ..service.auth import AuthResult, authorize_by_link
from ..keyboards import auth_menu, back_menu, main_menu
from ..render import (
    render_auth_already_bound,
    render_auth_ask_link,
    render_auth_success,
    render_auth_user_not_found,
    render_start_not_authorized,
)
from ..states import Auth

router = Router()


@router.callback_query(F.data == "auth:link")
async def cb_auth_link(call: CallbackQuery, state: FSMContext):
    await state.set_state(Auth.wait_link)
    await call.message.edit_text(
        render_auth_ask_link(),
        reply_markup=back_menu("menu:auth"),
    )
    await call.answer()


@router.callback_query(F.data == "menu:auth")
async def cb_back_to_auth(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        render_start_not_authorized(),
        reply_markup=auth_menu(),
    )
    await call.answer()


@router.message(Auth.wait_link)
async def msg_auth_link(message: Message, state: FSMContext):
    async with Session() as session:
        result, user = await authorize_by_link(
            session,
            Messenger.TELEGRAM,
            message.from_user.id,
            message.text or "",
        )

    if result == AuthResult.USER_NOT_FOUND:
        await message.answer(render_auth_user_not_found())
        return
    if result == AuthResult.ALREADY_BOUND:
        await message.answer(render_auth_already_bound())
        return

    await state.clear()
    await message.answer(render_auth_success())
    await message.answer("Главное меню", reply_markup=main_menu())
