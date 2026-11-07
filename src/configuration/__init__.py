from .endpoints.hysteria import HysteriaSettings
from .endpoints.mita import MitaSettings
from .endpoints.mtproxyl import MTProxyLSettings
from .endpoints.trusttunnel import TrustTunnelSettings
from .apps.tgbot import TelegramBotSettings
from .apps.reloader import ReloaderSettings
from .apps.payments import PaymentsSettings
from .apps.yoomoney import YoomoneySettings
from .other.proxy import ProxySettings
from .other.site.site import SiteSettings
from .other.site.nginx import NginxSettings
from .other.clash import ClashSettings
from .other.tls import TLSSettings
from .other.mihomo import MihomoSettings
from .aggregator import Settings


__all__ = [
    "Settings",
    "TLSSettings",
    "ProxySettings",
    "ClashSettings",
    "SiteSettings",
    "NginxSettings",
    "MitaSettings",
    "TrustTunnelSettings",
    "HysteriaSettings",
    "MTProxyLSettings",
    "YoomoneySettings",
    "MihomoSettings",
    "TelegramBotSettings",
    "ReloaderSettings",
    "PaymentsSettings",
]
