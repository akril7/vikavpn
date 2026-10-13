from src.settings.clash import ClashSettings
from src.settings.endpoints.hysteria import HysteriaSettings
from src.settings.endpoints.mita import MitaSettings
from src.settings.endpoints.mtproxyl import MTProxyLSettings
from src.settings.endpoints.trusttunnel import TrustTunnelSettings
from src.settings.apps.telegram import TelegramBotSettings
from src.settings.apps.reloader import ReloaderSettings
from src.settings.apps.payments import PaymentsSettings
from src.settings.apps.yoomoney import YoomoneySettings
from src.settings.site import SiteSettings
from src.settings.site.nginx import NginxSettings
from src.settings.tls import TLSSettings


class Settings:
    """Агрегатор всех настроек приложения.

    Все параметры опциональны. Если не переданы — создаются из .env.
    Переданные экземпляры используются как есть.
    """

    def __init__(
        self,
        *,
        tls_: TLSSettings | None = None,
        clash_: ClashSettings | None = None,
        site_: SiteSettings | None = None,
        nginx: NginxSettings | None = None,
        mita: MitaSettings | None = None,
        trusttunnel: TrustTunnelSettings | None = None,
        hysteria: HysteriaSettings | None = None,
        mtproxyl: MTProxyLSettings | None = None,
        yoomoney_: YoomoneySettings | None = None,
        telegram_bot: TelegramBotSettings | None = None,
        reloader: ReloaderSettings | None = None,
        payments: PaymentsSettings | None = None,
    ) -> None:
        self.tls = tls_ if tls_ is not None else TLSSettings()
        self.clash = clash_ if clash_ is not None else ClashSettings()
        self.yoomoney = yoomoney_ if yoomoney_ is not None else YoomoneySettings()

        self.site = site_ if site_ is not None else SiteSettings()
        self.nginx = nginx if nginx is not None else NginxSettings()

        self.mita = mita if mita is not None else MitaSettings()
        self.trusttunnel = trusttunnel if trusttunnel is not None else TrustTunnelSettings()
        self.hysteria = hysteria if hysteria is not None else HysteriaSettings()
        self.mtproxyl = mtproxyl if mtproxyl is not None else MTProxyLSettings()

        self.telegram_bot = telegram_bot if telegram_bot is not None else TelegramBotSettings()
        self.reloader = reloader if reloader is not None else ReloaderSettings()
        self.payments = payments if payments is not None else PaymentsSettings()


__all__ = [
    "Settings",
    "TLSSettings",
    "ClashSettings",
    "SiteSettings",
    "NginxSettings",
    "MitaSettings",
    "TrustTunnelSettings",
    "HysteriaSettings",
    "MTProxyLSettings",
    "YoomoneySettings",
    "TelegramBotSettings",
    "ReloaderSettings",
    "PaymentsSettings",
]
