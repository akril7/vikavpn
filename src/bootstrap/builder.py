from src.application.ports.registry import InstallTargets, ConfigureTargets, ControlTargets
from src.configuration import Settings
from src.infrastructure.app import AppInstaller, AppController
from src.infrastructure.services.clash import ClashConfigurator
from src.infrastructure.services.endpoints.hysteria import HysteriaInstaller, HysteriaController
from src.infrastructure.services.endpoints.mita import MitaInstaller, MitaConfigurator, MitaController
from src.infrastructure.services.endpoints.mtproxyl import MTProxyLInstaller, MTProxyLConfigurator
from src.infrastructure.services.endpoints.trusttunnel import TrustTunnelInstaller, TrustTunnelConfigurator
from src.infrastructure.services.mihomo.installer import MihomoInstaller
from src.infrastructure.services.site import SiteInstaller
from src.infrastructure.services.site.render import Mount
from src.infrastructure.systemd import SystemdUnitController


def build_services(settings: Settings) -> tuple[InstallTargets, ControlTargets, ConfigureTargets]:
    installers = {
        "mita": MitaInstaller(settings.mita),
        "hysteria": HysteriaInstaller(settings),
        "trusttunnel": TrustTunnelInstaller(settings.trusttunnel),
        "mtproxyl": MTProxyLInstaller(settings.mtproxyl, settings.tls, settings.proxy),
        "site": SiteInstaller(
            settings.site, settings.nginx, settings.tls,
            mounts=[
                Mount(settings.clash.configs_urlpath, str(settings.clash.configs_store_dir)),
                Mount(settings.payments.payment_path, settings.payments.origin, is_proxy=True)
            ]
        ),
        "mihomo": MihomoInstaller(settings.mihomo, settings.tls),
        "reloader": AppInstaller("reloader"),
        "payments": AppInstaller("payments"),
        "telegram_bot": AppInstaller("telegram_bot"),
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
        "mihomo": SystemdUnitController(
            settings.mihomo.service_name,
            build_is_installed_callback("mihomo")
        ),
        "reloader": AppController(
            "reloader",
            build_is_installed_callback("reloader")
        ),
        "payments": AppController(
            "payments",
            build_is_installed_callback("payments")
        ),
        "telegram_bot": AppController(
            "telegram_bot",
            build_is_installed_callback("telegram_bot")
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
            settings.trusttunnel, settings.tls, settings.proxy,
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
            settings.mita, build_is_installed_callback("mita"),
            settings.hysteria, build_is_installed_callback("hysteria"),
            settings.trusttunnel, build_is_installed_callback("trusttunnel"),
        ),
    }

    return installers, controllers, configurators
