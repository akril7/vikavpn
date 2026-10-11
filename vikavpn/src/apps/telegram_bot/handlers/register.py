from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.exc import IntegrityError

from src.core.reloader import Reloader
from src.db.connection import Session
from src.db.enums import Messenger
from src.db.repo import UserRepository, UserMessengerRepository
from src.db.repo.messager import MessengerAlreadyBoundError

from ..deps import get_user

from src.core.users.flow.registration import register_user
from ..keyboards import main_menu, platform_menu
from src.texts.render import render_platform_question, render_register_success, render_auth_already_bound, render_register_you, render_generate_unique_name_error
from ..states import Register

router = Router()


@router.callback_query(F.data == "auth:register")
async def cb_register(call: CallbackQuery, state: FSMContext):
    existing = await get_user(call.from_user.id)
    if existing is not None:
        await call.answer(render_auth_already_bound(), show_alert=True)
        return

    await state.set_state(Register.platform)
    await call.message.edit_text(
        render_platform_question(),
        reply_markup=platform_menu(),
    )
    await call.answer()


@router.callback_query(Register.platform, F.data.startswith("register:ios:"))
async def cb_register_platform(call: CallbackQuery, state: FSMContext, reloader: Reloader):
    ios = call.data.rsplit(":", 1)[-1] == "1"

    await state.clear()
    await call.message.edit_text(
        render_register_you()
    )

    async with Session() as session:
        user_repo = UserRepository(session)
        messager_repo = UserMessengerRepository(session)
        try:
            await register_user(
                user_repo,
                messager_repo,
                Messenger.TELEGRAM,
                call.from_user.id,
                ios_user=ios,
            )
        except MessengerAlreadyBoundError:
            await call.answer(render_auth_already_bound(), show_alert=True)
            return
        except IntegrityError:
            await call.answer(render_generate_unique_name_error(), show_alert=True)
            return

        await session.commit()
        reloader.schedule()

    await call.message.edit_text(
        render_register_success(),
    )
    await call.message.answer("Главное меню", reply_markup=main_menu())
    await call.answer()
