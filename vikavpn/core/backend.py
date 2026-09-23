from typing import ClassVar

from loguru import logger

from config import mita, trusttunnel, tls, hysteria, mtproxyl, webserver, clash, yoomoney, telegram_bot, cleanup
from database.models import Users

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
from services.backends.sub_cleanup import CleanupInstaller, CleanupService
from services.backends.telegram_bot import TelegramBotInstaller, TelegramBotService
from services.backends.trusttunnel import (
    TrustTunnelConfigurator,
    TrustTunnelInstaller,
    TrustTunnelService,
)
from services.backends.webserver import WebServerInstaller
from services.backends.yoomoney import YoomoneyInstaller, YoomoneyService


class Backend:
    __registry: ClassVar[dict[str, "Backend"]] = {}

    @classmethod
    def all(cls) -> dict[str, "Backend"]:
        return cls.__registry

    @classmethod
    def installed(cls) -> dict[str, "Backend"]:
        return dict(filter(lambda b: b[1].is_installed, cls.__registry.items()))

    def __init__(self,
                 name: str,
                 installer: Installer | None = None,
                 configurator: Configurator | None = None,
                 service: Service | None = None):
        self.__name = name
        self.__installer = installer
        self.__configurator = configurator
        self.__service = service

        type(self).__registry[name] = self

    @property
    def name(self) -> str:
        return self.__name

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

    def apply_config(self, users: Users):
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
                       MitaService())

TRUSTTUNNEL_BACKEND = Backend("trusttunnel",
                              TrustTunnelInstaller(trusttunnel),
                              TrustTunnelConfigurator(trusttunnel, tls),
                              TrustTunnelService(trusttunnel))

HYSTERIA_BACKEND = Backend("hysteria",
                           HysteriaInstaller(hysteria, tls),
                           HysteriaConfigurator(hysteria),
                           HysteriaService(hysteria))

MTPROXYL_BACKEND = Backend("mtproxyl",
                           MTProxyLInstaller(mtproxyl, tls),
                           MTProxyLConfigurator(mtproxyl),
                           MTProxyLService())

WEBSERVER_BACKEND = Backend("webserver",
                            installer=WebServerInstaller(webserver, tls))

CLASH_BACKEND = Backend("clash",
                        configurator=ClashConfigurator(clash, tls,
                                                       mita_config=mita,
                                                       hysteria_config=hysteria,
                                                       trusttunnel_config=trusttunnel))

YOOMONEY_BACKEND = Backend("yoomoney",
                           installer=YoomoneyInstaller(yoomoney),
                           service=YoomoneyService(yoomoney))

TELEGRAM_BOT_BACKEND = Backend("telegram-bot",
                               installer=TelegramBotInstaller(telegram_bot),
                               service=TelegramBotService(telegram_bot))

CLEANUP_BACKEND = Backend("cleanup",
                          installer=CleanupInstaller(cleanup),
                          service=CleanupService(cleanup),)
