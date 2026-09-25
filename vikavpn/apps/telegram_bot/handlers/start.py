from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.connection import Session
from database.enums import Messenger
from services.bot.auth import AuthResult, authorize_by_uuid
from ..deps import load_user
from ..keyboards import auth_menu, main_menu
from ..render import (
    render_auth_already_bound,
    render_auth_success,
    render_auth_user_not_found,
    render_start_not_authorized,
)

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deeplink(
    message: Message,
    command: CommandObject,
    state: FSMContext,
):
    await state.clear()
    payload = (command.args or "").strip()

    async with Session() as session:
        result, user = await authorize_by_uuid(
            session,
            Messenger.TELEGRAM,
            message.from_user.id,
            payload,
        )

    if result == AuthResult.USER_NOT_FOUND:
        await message.answer(render_auth_user_not_found())
        return
    if result == AuthResult.ALREADY_BOUND:
        await message.answer(render_auth_already_bound())
        return

    await message.answer(render_auth_success())
    await message.answer("Главное меню", reply_markup=main_menu())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await load_user(message.from_user.id)
    if user is None:
        await message.answer(
            render_start_not_authorized(),
            reply_markup=auth_menu(),
        )
        return
    await message.answer("Главное меню", reply_markup=main_menu())
