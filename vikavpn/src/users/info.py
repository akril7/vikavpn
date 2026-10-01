from src.core.url_build.file import build_clash_config_url, build_origin
from src.core.url_build.link import build_bot_auth_url, build_telegram_proxy_url
from src.db.connection import Session
from src.db.repo import UserRepository
from src.settings import Settings


async def get_user_info(name: str, settings: Settings) -> str:
    """Получить форматированную информацию о пользователе по имени."""
    async with Session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_name(name)
        if not user:
            raise RuntimeError(f"Пользователь {name} не найден")
        user = await repo.get_with_managed_users(user.id)

        origin = build_origin(settings.tls.domain, settings.site.port)

        clash_url = (
            build_clash_config_url(user, origin, settings.clash.configs_urlpath)
            if user.vpn_user else ""
        )
        tg_proxy_url = (
            build_telegram_proxy_url(
                user,
                settings.mtproxyl.sni,
                settings.tls.domain,
                settings.mtproxyl.port,
            )
            if user.proxy_user else ""
        )

        return (
            f"Информация о пользователе:\n"
            f"  Имя: {user.name}\n"
            f"  Пароль: {user.password}\n"
            f"  UUID: {user.uuid}\n"
            f"  Активен: {user.is_active}\n"
            f"  Использует прокси: {user.proxy_user}\n"
            f"  Использует VPN: {user.vpn_user}\n"
            f"  Использует IOS: {user.ios_user}\n"
            f"  Управляет: {', '.join(m.managed.name for m in user.managed_links)}\n"
            f"  Подписка истекает: {user.sub_expires_at:%d.%m.%Y %H:%M}\n"
            f"\n  Clash-ссылка:\n  {clash_url}\n"
            f"\n  TG-прокси:\n  {tg_proxy_url}\n"
            f"\n  Ссылка для входа в бота:\n  "
            f"{build_bot_auth_url(settings.telegram_bot.username, user)}\n"
        )
