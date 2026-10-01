from src.settings.clash import ClashSettings
from src.settings.endpoints.hysteria import HysteriaSettings
from src.settings.endpoints.mita import MitaSettings
from src.settings.endpoints.mtproxyl import MTProxyLSettings
from src.settings.endpoints.trusttunnel import TrustTunnelSettings
from src.settings.apps.disabler import DisablerSettings
from src.settings.apps.telegram import TelegramBotSettings
from src.settings.apps.webhook import WebhookSettings
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
        tls: TLSSettings | None = None,
        clash: ClashSettings | None = None,
        site: SiteSettings | None = None,
        nginx: NginxSettings | None = None,
        mita: MitaSettings | None = None,
        trusttunnel: TrustTunnelSettings | None = None,
        hysteria: HysteriaSettings | None = None,
        mtproxyl: MTProxyLSettings | None = None,
        yoomoney: YoomoneySettings | None = None,
        telegram_bot: TelegramBotSettings | None = None,
        disabler: DisablerSettings | None = None,
        webhook: WebhookSettings | None = None,
    ) -> None:
        self.tls = tls if tls is not None else TLSSettings()
        self.clash = clash if clash is not None else ClashSettings()
        self.webhook = webhook if webhook is not None else WebhookSettings()

        self.site = site if site is not None else SiteSettings()
        self.nginx = nginx if nginx is not None else NginxSettings()

        self.mita = mita if mita is not None else MitaSettings()
        self.trusttunnel = trusttunnel if trusttunnel is not None else TrustTunnelSettings()
        self.hysteria = hysteria if hysteria is not None else HysteriaSettings()
        self.mtproxyl = mtproxyl if mtproxyl is not None else MTProxyLSettings()

        self.yoomoney = yoomoney if yoomoney is not None else YoomoneySettings()
        self.telegram_bot = telegram_bot if telegram_bot is not None else TelegramBotSettings()
        self.disabler = disabler if disabler is not None else DisablerSettings()


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
    "DisablerSettings",
    "WebhookSettings",
]