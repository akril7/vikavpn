from typing import Callable

from loguru import logger
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from src.application.ports.services import Installer
from src.application.ports.services.callables import IsInstallCallback
from src.bootstrap.service import Service
from src.configuration import Settings
from src.infrastructure.app import AppInstaller, AppController
import src.infrastructure.services.clash as clash
import src.infrastructure.services.endpoints.mita as mita
import src.infrastructure.services.endpoints.mtproxyl as mtproxyl
import src.infrastructure.services.endpoints.trusttunnel as trusttunnel
import src.infrastructure.services.mihomo as mihomo
import src.infrastructure.services.site as site
from src.infrastructure.services import microwarp
from src.infrastructure.services.site.render import Mount
from src.infrastructure.systemd import SystemdUnitController


def build_is_install_callback(installer: Installer) -> IsInstallCallback:
    return lambda: installer.is_installed


def check_required_settings(get: Callable[[], tuple[BaseSettings, ...]]) -> bool:
    try:
        get()
    except ValidationError:
        logger.debug(f"Settings are not filled")
        return False
    return True


def build_mita(settings: Settings) -> Service:
    installer = None
    controller = None
    configurator = None

    if check_required_settings(lambda: (settings.mita,)):
        installer = mita.MitaInstaller(settings.mita)
        is_install_callback = build_is_install_callback(installer)
        controller = mita.MitaController(is_install_callback=is_install_callback)
        configurator = mita.MitaConfigurator(
            settings.mita,
            is_install_callback=is_install_callback,
            reload_controller_callback=controller.reload,
        )

    return Service(installer=installer, controller=controller, configurator=configurator, logname="mita")


def build_mtproxyl(settings: Settings) -> Service:
    installer = None
    controller = None
    configurator = None

    if check_required_settings(
            lambda: (settings.mtproxyl, settings.tls, settings.proxy, settings.site)
    ):
        installer = mtproxyl.MTProxyLInstaller(
            settings.mtproxyl, settings.tls, settings.proxy, settings.site
        )
        is_install_callback = build_is_install_callback(installer)
        controller = SystemdUnitController(
            settings.mtproxyl.service_name,
            is_install_callback=is_install_callback,
        )
        configurator = mtproxyl.MTProxyLConfigurator(
            settings.mtproxyl,
            is_install_callback=is_install_callback,
            reload_controller_callback=controller.reload,
        )

    return Service(installer=installer, controller=controller, configurator=configurator, logname="mtproxyl")


def build_trusttunnel(settings: Settings) -> Service:
    installer = None
    controller = None
    configurator = None

    if check_required_settings(lambda: (settings.trusttunnel, settings.tls, settings.proxy)):
        installer = trusttunnel.TrustTunnelInstaller(settings.trusttunnel)
        is_install_callback = build_is_install_callback(installer)
        controller = SystemdUnitController(
            settings.trusttunnel.service_name,
            is_install_callback=is_install_callback,
        )
        configurator = trusttunnel.TrustTunnelConfigurator(
            settings.trusttunnel,
            settings.tls,
            settings.proxy,
            is_install_callback=is_install_callback,
            reload_controller_callback=controller.reload,
        )

    return Service(installer=installer, controller=controller, configurator=configurator, logname="trusttunnel")


def build_site(settings: Settings) -> Service:
    installer = None
    controller = None

    if check_required_settings(
            lambda: (settings.site, settings.nginx, settings.tls,
                     settings.clash, settings.payments)
    ):
        installer = site.SiteInstaller(
            settings.site, settings.nginx, settings.tls,
            mounts=[
                Mount(settings.clash.configs_urlpath, str(settings.clash.configs_store_dir)),
                Mount(settings.payments.payment_path, settings.payments.origin, is_proxy=True),
            ],
        )
        is_install_callback = build_is_install_callback(installer)
        controller = SystemdUnitController(
            settings.nginx.service_name,
            is_install_callback=is_install_callback,
        )

    return Service(installer=installer, controller=controller, logname="site")


def build_mihomo(settings: Settings) -> Service:
    installer = None
    controller = None

    if check_required_settings(lambda: (settings.mihomo, settings.tls)):
        installer = mihomo.MihomoInstaller(
            settings.mihomo, settings.tls
        )
        is_install_callback = build_is_install_callback(installer)
        controller = SystemdUnitController(
            settings.mihomo.service_name,
            is_install_callback=is_install_callback,
        )

    return Service(installer=installer, controller=controller, logname="mihomo")


def build_clash(
        settings: Settings,
        mita_is_installed_callback: IsInstallCallback,
        trusttunnel_is_installed_callback: IsInstallCallback
) -> Service:
    configurator = None

    if check_required_settings(
            lambda: (settings.clash, settings.tls,
                     settings.mita, settings.trusttunnel)
    ):
        configurator = clash.ClashConfigurator(
            settings.clash, settings.tls,
            settings.mita, mita_is_installed_callback,
            settings.trusttunnel, trusttunnel_is_installed_callback
        )

    return Service(configurator=configurator, logname="clash")


def build_microwarp(settings: Settings):
    installer = None

    if check_required_settings(lambda: (settings.microwarp, )):
        installer = microwarp.MicrowarpInstaller(settings.microwarp)

    return Service(installer=installer, logname="microwarp")


def build_app(app_name: str, get_settings) -> Service:
    installer = None
    controller = None

    if check_required_settings(get_settings):
        installer = AppInstaller(app_name)
        is_install_callback = build_is_install_callback(installer)
        controller = AppController(app_name, is_install_callback=is_install_callback)

    return Service(installer=installer, controller=controller, logname=app_name)


def build_reloader(settings: Settings) -> Service:
    return build_app("reloader", lambda: (settings.reloader,))


def build_payments(settings: Settings) -> Service:
    return build_app("payments", lambda: (settings.reloader, settings.payments, settings.yoomoney))


def build_telegram_bot(settings: Settings) -> Service:
    return build_app("telegram_bot",
                     lambda: (settings.telegram_bot, settings.proxy,
                              settings.yoomoney, settings.site,
                              settings.tls), )


def build_services(settings: Settings) -> dict[str, Service]:
    services: dict[str, Service] = {
        "mita": build_mita(settings),
        "mtproxyl": build_mtproxyl(settings),
        "trusttunnel": build_trusttunnel(settings),
        "microwarp": build_microwarp(settings),
        "site": build_site(settings),
        "mihomo": build_mihomo(settings),
        "reloader": build_reloader(settings),
        "payments": build_payments(settings),
        "telegram_bot": build_telegram_bot(settings),
    }
    services["clash"] = build_clash(settings,
                                    build_is_install_callback(services["mita"].installer),
                                    build_is_install_callback(services["trusttunnel"].installer))
    return services
