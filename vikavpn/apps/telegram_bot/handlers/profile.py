from aiogram import F, Router
from aiogram.types import CallbackQuery

from config.app import SNI
from config import clash, mtproxyl, tls
from services.bot.profile import build_profile

from ..deps import load_user_with_managed
from ..keyboards import profile_menu
from ..render import render_profile

router = Router()


@router.callback_query(F.data == "menu:profile")
async def cb_profile(call: CallbackQuery):
    user = await load_user_with_managed(call.from_user.id)
    if user is None:
        await call.answer("Пользователь не найден", show_alert=True)
        return

    profile = build_profile(
        user,
        domain=tls.domain,
        clash_path=clash.url_config_path,
        sni=SNI,
        mtproxyl_port=mtproxyl.port,
    )

    await call.message.edit_text(
        render_profile(profile),
        reply_markup=profile_menu(profile.tg_proxy_url, profile.clash_url),
    )
    await call.answer()
