from .endpoints.hysteria import HysteriaSettings
from .endpoints.mita import MitaSettings
from .endpoints.mtproxyl import MTProxyLSettings
from .endpoints.trusttunnel import TrustTunnelSettings
from .apps.telegram import TelegramBotSettings
from .apps.reloader import ReloaderSettings
from .apps.payments import PaymentsSettings
from .apps.yoomoney import YoomoneySettings
from .other.site.site import SiteSettings
from .other.site.nginx import NginxSettings
from .other.clash import ClashSettings
from .other.tls import TLSSettings
from .other.trustclient import TrustClientSettings
from .aggregator import Settings


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
    "TrustClientSettings",
    "TelegramBotSettings",
    "ReloaderSettings",
    "PaymentsSettings",
]
