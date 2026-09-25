from typing import ClassVar

from loguru import logger

from services.backends.pyrun import AppInstaller
from services.backends.systemd import SystemdService
from settings import mita, trusttunnel, tls, hysteria, mtproxyl, webserver, clash, yoomoney, telegram_bot, cleanup
from database.models import User

from services.backends.base import (
    Configurator,
    Installer,
    Service
)
from services.backends.clash_config import ClashConfigurator
from services.backends.hysteria import (
    HysteriaConfigurator,
    HysteriaInstaller,
    HysteriaService,
)
from services.backends.mita import MitaConfigurator, MitaInstaller, MitaService
from services.backends.mtproxyl import (
    MTProxyLConfigurator,
    MTProxyLInstaller,
    MTProxyLService,
)
from services.backends.trusttunnel import (
    TrustTunnelConfigurator,
    TrustTunnelInstaller
)
from services.backends.webserver import WebServerInstaller


class Backend:
    __registry: ClassVar[dict[str, "Backend"]] = {}

    @classmethod
    def all(cls) -> dict[str, "Backend"]:
        return cls.__registry

    @classmethod
    def installed(cls) -> dict[str, "Backend"]:
        return dict(filter(lambda b: b[1].is_installed, cls.__registry.items()))

    @classmethod
    def endpoints(cls) -> dict[str, "Backend"]:
        return dict(filter(lambda b: b[1].is_endpoint and b[1].is_installed, cls.__registry.items()))

    def __init__(self,
                 name: str,
                 installer: Installer | None = None,
                 configurator: Configurator | None = None,
                 service: Service | None = None,
                 is_endpoint: bool = False):
        self.__name = name
        self.__installer = installer
        self.__configurator = configurator
        self.__service = service
        self.__is_endpoint = is_endpoint

        type(self).__registry[name] = self

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_endpoint(self) -> bool:
        return self.__is_endpoint

    @property
    def is_installed(self) -> bool:
        if not self.__installer:
            return False

        return self.__installer.is_installed

    @property
    def installer(self) -> Installer | None:
        return self.__installer

    @property
    def configurator(self) -> Configurator | None:
        return self.__configurator

    @property
    def service(self) -> Service | None:
        return self.__service

    def install(self, force: bool = False):
        if not self.__installer:
            logger.warning(f"{self.name} не поддерживает установку")
            return

        if self.__installer.is_installed and not force:
            logger.info(f"{self.name} уже установлен")
            return

        logger.info(f"Установка {self.name}")
        self.__installer.install(force=force)

    def uninstall(self):
        if not self.__installer:
            logger.warning(f"{self.name} не поддерживает удаление")
            return

        if not self.__installer.is_installed:
            logger.info(f"{self.name} не установлен")
            return

        logger.info(f"Удаляем {self.name}")
        self.__installer.uninstall()

    def apply_config(self, users: list[User]):
        if not self.__configurator:
            logger.warning(f"{self.name} не поддерживает применение конфигурации")
            return

        if self.__installer and not self.is_installed:
            logger.warning(f"{self.name} не установлен")
            return

        logger.info(f"Применяем настроки для {self.name}")
        self.__configurator.apply(users=users)


MITA_BACKEND = Backend("mita",
                       MitaInstaller(mita),
                       MitaConfigurator(mita),
                       MitaService(),
                       is_endpoint=True)

TRUSTTUNNEL_BACKEND = Backend("trusttunnel",
                              TrustTunnelInstaller(trusttunnel),
                              TrustTunnelConfigurator(trusttunnel, tls),
                              SystemdService(trusttunnel.service),
                              is_endpoint=True)

HYSTERIA_BACKEND = Backend("hysteria",
                           HysteriaInstaller(hysteria, tls),
                           HysteriaConfigurator(hysteria),
                           HysteriaService(hysteria),
                           is_endpoint=True)

MTPROXYL_BACKEND = Backend("mtproxyl",
                           MTProxyLInstaller(mtproxyl, tls),
                           MTProxyLConfigurator(mtproxyl),
                           MTProxyLService(),
                           is_endpoint=True)

WEBSERVER_BACKEND = Backend("webserver",
                            installer=WebServerInstaller(webserver, tls))

CLASH_BACKEND = Backend("clash",
                        configurator=ClashConfigurator(clash, tls, webserver,
                                                       mita_config=mita,
                                                       hysteria_config=hysteria,
                                                       trusttunnel_config=trusttunnel))

YOOMONEY_BACKEND = Backend("yoomoney",
                           installer=AppInstaller("yoomoney_webhook",
                                                  "VIKAVPN Yoomoney webhook",
                                                  yoomoney.webhook_service),
                           service=SystemdService(yoomoney.webhook_service))

TELEGRAM_BOT_BACKEND = Backend("telegram-bot",
                               installer=AppInstaller("telegram_bot",
                                                      "VIKAVPN Telegram bot",
                                                      telegram_bot.service),
                               service=SystemdService(telegram_bot.service))

CLEANUP_BACKEND = Backend("cleanup",
                          installer=AppInstaller("cleanup",
                                                 "VIKAVPN expire subs cleanup",
                                                 cleanup.service),
                          service=SystemdService(cleanup.service))
