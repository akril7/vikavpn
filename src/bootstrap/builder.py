from src.application.ports.registry import InstallTargets, ConfigureTargets, ControlTargets
from src.configuration import Settings
from src.infrastructure.app import AppInstaller, AppController
from src.infrastructure.services.clash import ClashConfigurator
from src.infrastructure.services.endpoints.hysteria import HysteriaInstaller, HysteriaController
from src.infrastructure.services.endpoints.mita import MitaInstaller, MitaConfigurator, MitaController
from src.infrastructure.services.endpoints.mtproxyl import MTProxyLInstaller, MTProxyLConfigurator
from src.infrastructure.services.endpoints.trusttunnel import TrustTunnelInstaller, TrustTunnelConfigurator
from src.infrastructure.services.site import SiteInstaller
from src.infrastructure.services.trustclient.installer import TrustClientInstaller
from src.infrastructure.systemd import SystemdUnitController


def build_services(settings: Settings) -> tuple[InstallTargets, ControlTargets, ConfigureTargets]:
    installers = {
        "mita": MitaInstaller(settings.mita),
        "hysteria": HysteriaInstaller(settings),
        "trusttunnel": TrustTunnelInstaller(settings.trusttunnel),
        "mtproxyl": MTProxyLInstaller(settings.mtproxyl, settings.tls),
        "site": SiteInstaller(settings),
        "trustclient": TrustClientInstaller(settings.trustclient),
        "reloader": AppInstaller("reloader"),
        "payments": AppInstaller("payments")
    }

    def build_is_installed_callback(name):
        return lambda: installers[name].is_installed

    controllers = {
        "mita": MitaController(
            build_is_installed_callback("mita")
        ),
        "hysteria": HysteriaController(
            settings.hysteria,
            build_is_installed_callback("hysteria")
        ),
        "mtproxyl": SystemdUnitController(
            settings.mtproxyl.service_name,
            build_is_installed_callback("mtproxyl")
        ),
        "trusttunnel": SystemdUnitController(
            settings.trusttunnel.service_name,
            build_is_installed_callback("trusttunnel")
        ),
        "trustclient": SystemdUnitController(
            settings.trustclient.service_name,
            build_is_installed_callback("trustclient")
        ),
        "reloader": AppController(
            "reloader",
            build_is_installed_callback("reloader")
        ),
        "payments": AppController(
            "payments",
            build_is_installed_callback("payments")
        ),
        "tgbot": AppController(
            "telegram_bot",
            build_is_installed_callback("tgbot")
        ),
    }

    def build_reload_callback(name: str):
        return controllers[name].reload

    configurators = {
        "mita": MitaConfigurator(
            settings.mita,
            build_is_installed_callback("mita"),
            build_reload_callback("mita")
        ),
        "trusttunnel": TrustTunnelConfigurator(
            settings.trusttunnel, settings.tls,
            build_is_installed_callback("trusttunnel"),
            build_reload_callback("trusttunnel")
        ),
        "mtproxyl": MTProxyLConfigurator(
            settings.mtproxyl,
            build_is_installed_callback("trusttunnel"),
            build_reload_callback("trusttunnel")
        ),
        "clash": ClashConfigurator(
            settings.clash, settings.tls,
            settings.mita, settings.hysteria,
            settings.trusttunnel),
    }

    return installers, controllers, configurators
