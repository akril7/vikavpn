from src.configuration.endpoints.hysteria import HysteriaSettings
from src.configuration.endpoints.mita import MitaSettings
from src.configuration.endpoints.mtproxyl import MTProxyLSettings
from src.configuration.endpoints.trusttunnel import TrustTunnelSettings
from src.configuration.apps.telegram import TelegramBotSettings
from src.configuration.apps.reloader import ReloaderSettings
from src.configuration.apps.payments import PaymentsSettings
from src.configuration.apps.yoomoney import YoomoneySettings
from src.configuration.other.site import SiteSettings
from src.configuration.other.site.nginx import NginxSettings
from src.configuration.other.tls import TLSSettings
from src.configuration.other.trustclient import TrustClientSettings
from src.configuration.other.clash import ClashSettings


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
        trustclient: TrustClientSettings | None = None,
        telegram_bot: TelegramBotSettings | None = None,
        reloader: ReloaderSettings | None = None,
        payments: PaymentsSettings | None = None,
    ) -> None:
        self.__tls = tls
        self.__clash = clash
        self.__yoomoney = yoomoney

        self.__site = site
        self.__nginx = nginx
        self.__trustclient = trustclient

        self.__mita = mita
        self.__trusttunnel = trusttunnel
        self.__hysteria = hysteria
        self.__mtproxyl = mtproxyl

        self.__telegram_bot = telegram_bot
        self.__reloader = reloader
        self.__payments = payments

    @property
    def tls(self) -> TLSSettings:
        if self.__tls is None:
            self.__tls = TLSSettings()
        return self.__tls

    @property
    def clash(self) -> ClashSettings:
        if self.__clash is None:
            self.__clash = ClashSettings()
        return self.__clash

    @property
    def site(self) -> SiteSettings:
        if self.__site is None:
            self.__site = SiteSettings()
        return self.__site

    @property
    def nginx(self) -> NginxSettings:
        if self.__nginx is None:
            self.__nginx = NginxSettings()
        return self.__nginx

    @property
    def mita(self) -> MitaSettings:
        if self.__mita is None:
            self.__mita = MitaSettings()
        return self.__mita

    @property
    def trusttunnel(self) -> TrustTunnelSettings:
        if self.__trusttunnel is None:
            self.__trusttunnel = TrustTunnelSettings()
        return self.__trusttunnel

    @property
    def hysteria(self) -> HysteriaSettings:
        if self.__hysteria is None:
            self.__hysteria = HysteriaSettings()
        return self.__hysteria

    @property
    def mtproxyl(self) -> MTProxyLSettings:
        if self.__mtproxyl is None:
            self.__mtproxyl = MTProxyLSettings()
        return self.__mtproxyl

    @property
    def yoomoney(self) -> YoomoneySettings:
        if self.__yoomoney is None:
            self.__yoomoney = YoomoneySettings()
        return self.__yoomoney

    @property
    def trustclient(self) -> TrustClientSettings:
        if self.__trustclient is None:
            self.__trustclient = TrustClientSettings()
        return self.__trustclient

    @property
    def telegram_bot(self) -> TelegramBotSettings:
        if self.__telegram_bot is None:
            self.__telegram_bot = TelegramBotSettings()
        return self.__telegram_bot

    @property
    def reloader(self) -> ReloaderSettings:
        if self.__reloader is None:
            self.__reloader = ReloaderSettings()
        return self.__reloader

    @property
    def payments(self) -> PaymentsSettings:
        if self.__payments is None:
            self.__payments = PaymentsSettings()
        return self.__payments
