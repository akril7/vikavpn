from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.core.users.flow.profile import build_profile
from src.db.repo import options
from src.settings import Settings

from ..deps import get_user
from ..keyboards import profile_menu
from src.texts.render import render_profile

router = Router()


@router.callback_query(F.data == "menu:profile")
async def cb_profile(call: CallbackQuery, settings: Settings):
    user = await get_user(call.from_user.id, options=options.messenger_options() + options.managed_options())
    if user is None:
        await call.answer("Пользователь не найден", show_alert=True)
        return

    profile = build_profile(user, settings)

    await call.message.edit_text(
        render_profile(profile),
        reply_markup=profile_menu(profile.tg_proxy_url, profile.clash_url),
    )
    await call.answer()
