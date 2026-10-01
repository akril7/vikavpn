from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.core.url_build.file import build_clash_video_guide_url, build_origin
from src.settings import Settings
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
async def cb_help(call: CallbackQuery, state: FSMContext, settings: Settings):
    await state.clear()
    origin = build_origin(settings.tls.domain, settings.site.port)
    video_url = build_clash_video_guide_url(origin)
    await call.message.edit_text(
        render_help(video_url, settings.telegram_bot.admin_username),
        reply_markup=back_menu("menu:main"),
    )
    await call.answer()
