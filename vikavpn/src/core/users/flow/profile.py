from dataclasses import dataclass
from datetime import datetime

from src.db.models import User
from src.settings import Settings
from src.settings.app import TZ
from src.core.utils.dt import utcnow
from src.core.url_build.file import build_origin, build_clash_config_url
from src.core.url_build.link import build_telegram_proxy_url


@dataclass(frozen=True)
class ProfileView:
    name: str
    password: str
    expires_at: datetime
    is_active: bool
    days_left: int
    tariff_label: str
    telegram_id: int
    clash_url: str | None
    tg_proxy_url: str | None
    managed_names: list[str]


def tariff_label(user: User) -> str:
    if user.vpn_user and user.proxy_user:
        return "VPN + TG Proxy"
    if user.vpn_user:
        return "VPN"
    if user.proxy_user:
        return "TG Proxy"
    return "—"


def build_profile(user: User, settings: Settings) -> ProfileView:
    """
    Собрать представление профиля пользователя для отображения в боте.

    Формирует ``ProfileView`` на основе данных пользователя и настроек
    приложения: рассчитывает остаток дней подписки, строит URL-ы для
    подключения (Clash-подписка и Telegram-прокси) и собирает имена
    управляемых пользователей.

    URL-ы строятся только для тех сервисов, которые включены у пользователя
    (``user.vpn_user`` / ``user.proxy_user``). Для отключённых сервисов
    соответствующее поле будет ``None``.

    Функция предполагает, что у ``user`` уже загружены связи
    ``managed_links`` и ``messenger_links`` (например, через
    ``options.managed_options()`` + ``options.messenger_options()``).
    Иначе обращение к ``user.managed_links`` / ``user.telegram_id``
    вызовет ``InvalidRequestError`` из-за ``lazy="raise"``.

    Args:
        user: Пользователь с загруженными связями ``managed_links``
            и ``messenger_links``.
        settings: Настройки приложения (домен, порты, пути URL-ов).

    Returns:
        Заполненный ``ProfileView`` с рассчитанными полями
        ``expires_at`` (в локальной TZ), ``days_left``, ``is_active``,
        ``tariff_label``, ``clash_url``, ``tg_proxy_url``
        и ``managed_names``.
    """
    now = utcnow()
    days_left = max(0, (user.sub_expires_at.date() - now.date()).days)

    origin = build_origin(settings.tls.domain, settings.site.port)
    clash_url = build_clash_config_url(user, origin, settings.clash.configs_urlpath) if user.vpn_user else None
    tg_proxy_url = build_telegram_proxy_url(user,
                                            settings.mtproxyl.sni,
                                            settings.tls.domain,
                                            settings.mtproxyl.port) if user.proxy_user else None

    managed_names = [u.managed.name for u in user.managed_links if u.managed]

    return ProfileView(
        name=user.name,
        password=user.password,
        expires_at=user.sub_expires_at.astimezone(TZ),
        is_active=user.is_active,
        days_left=days_left,
        tariff_label=tariff_label(user),
        telegram_id=user.telegram_id,
        clash_url=clash_url,
        tg_proxy_url=tg_proxy_url,
        managed_names=managed_names,
    )
