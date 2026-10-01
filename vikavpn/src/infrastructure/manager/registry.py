from functools import lru_cache
from typing import Any

from src.core.interfaces import Installer, Configurator, Controller
from src.infrastructure.app import AppInstaller, AppController
from src.infrastructure.services.clash import ClashConfigurator
from src.infrastructure.services.endpoints.hysteria import HysteriaInstaller, HysteriaController
from src.infrastructure.services.endpoints.mita import MitaInstaller, MitaConfigurator, MitaController
from src.infrastructure.services.endpoints.mtproxyl import MTProxyLInstaller, MTProxyLConfigurator, MTProxyLController
from src.infrastructure.services.endpoints.trusttunnel import TrustTunnelInstaller, TrustTunnelConfigurator
from src.infrastructure.services.site import SiteInstaller
from src.infrastructure.systemd import SystemdUnitController
from src.settings import Settings

InstallTargets = dict[str, Installer]
ConfigureTargets = dict[str, Configurator]
ControlTargets = dict[str, Controller]
AnyTargets = InstallTargets | ConfigureTargets | ControlTargets


class Registry:
    def __init__(self, settings: Settings):
        self.__settings = settings
        self.__installer_targets = _build_installers(settings)
        self.__configurator_targets = _build_configurators(settings)
        self.__controller_targets = _build_controllers(settings)

    @property
    def settings(self) -> Settings:
        return self.__settings

    def get_install_targets(self, names: list[str] | None = None) -> InstallTargets:
        return _filter(self.__installer_targets, names)

    def get_control_targets(self, names: list[str] | None = None) -> ControlTargets:
        return _filter(self.__controller_targets, names)

    def get_configure_targets(self, names: list[str] | None = None) -> ConfigureTargets:
        return _filter(self.__configurator_targets, names)


@lru_cache(maxsize=1)
def _build_installers(settings: Settings):
    return {
        "mita": MitaInstaller(settings.mita),
        "hysteria": HysteriaInstaller(settings.hysteria, settings.tls, settings.site, settings.webhook),
        "trusttunnel": TrustTunnelInstaller(settings.trusttunnel),
        "mtproxyl": MTProxyLInstaller(settings.mtproxyl, settings.tls),
        "site": SiteInstaller(settings.site, settings.tls, settings.clash, settings.webhook, settings.nginx),
        "tgbot": AppInstaller("telegram_bot"),
        "disabler": AppInstaller("disabler"),
        "webhook": AppInstaller("webhook"),
    }


@lru_cache(maxsize=1)
def _build_configurators(settings: Settings):
    return {
        "mita": MitaConfigurator(settings.mita),
        "trusttunnel": TrustTunnelConfigurator(settings.trusttunnel, settings.tls),
        "mtproxyl": MTProxyLConfigurator(settings.mtproxyl),
        "clash": ClashConfigurator(settings.clash, settings.tls, settings.site,
                                   settings.mita, settings.hysteria, settings.trusttunnel),
    }


@lru_cache(maxsize=1)
def _build_controllers(settings: Settings):
    return {
        "mita": MitaController(),
        "hysteria": HysteriaController(settings.hysteria),
        "mtproxyl": MTProxyLController(settings.mtproxyl),
        "trusttunnel": SystemdUnitController(settings.trusttunnel.service_name),
        "tgbot": AppController("telegram_bot"),
        "disabler": AppController("disabler"),
        "webhook": AppController("webhook"),
    }


def _filter(storage: AnyTargets, names: list[str] | None = None) -> dict[str, Any]:
    if not names:
        return dict(storage.items())

    for name in names:
        if name not in storage:
            raise ValueError(f"Цели с именем {name} не существует")

    return dict(filter(lambda v: v[0] in names, storage.items()))
