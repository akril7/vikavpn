from src.configuration.endpoints.mita import MitaSettings
from src.configuration.endpoints.mtproxyl import MTProxyLSettings
from src.configuration.endpoints.trusttunnel import TrustTunnelSettings
from src.configuration.apps.tgbot import TelegramBotSettings
from src.configuration.apps.reloader import ReloaderSettings
from src.configuration.apps.payments import PaymentsSettings
from src.configuration.apps.yoomoney import YoomoneySettings
from src.configuration.other.proxy import ProxySettings
from src.configuration.other.site import SiteSettings
from src.configuration.other.site.nginx import NginxSettings
from src.configuration.other.tls import TLSSettings
from src.configuration.other.mihomo import MihomoSettings
from src.configuration.other.clash import ClashSettings


class Settings:
    """Агрегатор всех настроек приложения.

    Все параметры опциональны. Если не переданы — создаются из .env.
    Переданные экземпляры используются как есть.
    """

    def __init__(self, **kwargs):
        self.__settings = kwargs

    def __get(self, name: str, default_cls):
        if self.__settings.get(name) is None:
            self.__settings[name] = default_cls()
        return self.__settings[name]

    @property
    def tls(self) -> TLSSettings: return self.__get("tls", TLSSettings)

    @property
    def clash(self) -> ClashSettings: return self.__get("clash", ClashSettings)

    @property
    def proxy(self) -> ProxySettings: return self.__get("proxy", ProxySettings)

    @property
    def site(self) -> SiteSettings: return self.__get("site", SiteSettings)

    @property
    def nginx(self) -> NginxSettings: return self.__get("nginx", NginxSettings)

    @property
    def mita(self) -> MitaSettings: return self.__get("mita", MitaSettings)

    @property
    def trusttunnel(self) -> TrustTunnelSettings: return self.__get("trusttunnel", TrustTunnelSettings)

    @property
    def mtproxyl(self) -> MTProxyLSettings: return self.__get("mtproxyl", MTProxyLSettings)

    @property
    def yoomoney(self) -> YoomoneySettings: return self.__get("yoomoney", YoomoneySettings)

    @property
    def telegram_bot(self) -> TelegramBotSettings: return self.__get("telegram_bot", TelegramBotSettings)

    @property
    def reloader(self) -> ReloaderSettings: return self.__get("reloader", ReloaderSettings)

    @property
    def payments(self) -> PaymentsSettings: return self.__get("payments", PaymentsSettings)

    @property
    def mihomo(self) -> MihomoSettings: return self.__get("mihomo", MihomoSettings)
