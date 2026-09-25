from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from settings import telegram_bot, webserver
from services.url_build import build_clash_video_guide_url
from ..deps import load_user
from ..keyboards import auth_menu, main_menu, back_menu
from ..render import render_start_not_authorized, render_help

router = Router()


@router.callback_query(F.data == "menu:main")
async def cb_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await load_user(call.from_user.id)
    if user is None:
        await call.message.edit_text(
            render_start_not_authorized(),
            reply_markup=auth_menu(),
        )
        await call.answer()
        return

    await call.message.edit_text("Главное меню", reply_markup=main_menu())
    await call.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        render_help(build_clash_video_guide_url(webserver.server), telegram_bot.admin_username),
        reply_markup=back_menu("menu:main"),
    )
    await call.answer()
