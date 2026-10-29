from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.db.connection import Session
from src.db.enums import Messenger
from src.db.models import User
from src.db.repo import UserRepository, UserMessengerRepository

from src.core.users.flow.auth import AuthResult, authorize_by_uuid

from ..deps import get_user
from ..keyboards import auth_menu, main_menu
from src.texts.render import (
    render_auth_user_not_found,
    render_start_not_authorized,
    render_auth_already_bound
)

router = Router()


async def show_start(user: User, message: Message):
    if user is None:
        await message.answer(
            render_start_not_authorized(),
            reply_markup=auth_menu(),
        )
        return
    await message.answer("Главное меню", reply_markup=main_menu())


@router.message(CommandStart(deep_link=True))
async def cmd_start_deeplink(
    message: Message,
    command: CommandObject,
    state: FSMContext,
):
    await state.clear()
    payload = (command.args or "").strip()

    async with Session() as session:
        user_repo = UserRepository(session)
        messager_repo = UserMessengerRepository(session)
        result, user = await authorize_by_uuid(
            user_repo,
            messager_repo,
            Messenger.TELEGRAM,
            message.from_user.id,
            payload,
        )
        await session.commit()

    if result == AuthResult.USER_NOT_FOUND:
        await message.answer(render_auth_user_not_found())
        return
    elif result == AuthResult.ALREADY_BOUND:
        await message.answer(render_auth_already_bound())
        return

    await show_start(user, message)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    await show_start(user, message)


@router.message(F.text)
async def msg_fallback(message: Message, state: FSMContext):
    """Ловит любой текст, который не поймали другие хендлеры.

    Логика:
    - Если пользователь в FSM-состоянии — не мешаем (пусть вводит данные).
    - Если пользователь не привязан — показываем auth-меню.
    - Если привязан — показываем главное меню.
    """
    current_state = await state.get_state()
    if current_state is not None:
        return

    user = await get_user(message.from_user.id)

    if user is None:
        await message.answer(
            render_start_not_authorized(),
            reply_markup=auth_menu(),
        )
        return

    await message.answer(
        "Главное меню",
        reply_markup=main_menu(),
    )
