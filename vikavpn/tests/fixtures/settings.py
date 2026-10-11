import pytest

from src.settings import Settings
from src.settings.apps.telegram import TelegramBotSettings
from src.settings.apps.webhook import WebhookSettings
from src.settings.apps.yoomoney import YoomoneySettings
from src.settings.clash import ClashSettings
from src.settings.endpoints.hysteria import HysteriaSettings
from src.settings.endpoints.mita import MitaSettings
from src.settings.endpoints.mtproxyl import MTProxyLSettings
from src.settings.endpoints.trusttunnel import TrustTunnelSettings
from src.settings.site import SiteSettings
from src.settings.site.nginx import NginxSettings
from src.settings.tls import TLSSettings


@pytest.fixture
def fake_tls(tmp_path):
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("dummy-cert")
    key.write_text("dummy-key")
    return TLSSettings(domain="test.local", cert_path=cert, key_path=key)


@pytest.fixture
def settings(fake_tls, tmp_path):
    return Settings(
        tls_=fake_tls,
        clash_=ClashSettings(configs_store_dir=tmp_path / "clash"),
        site_=SiteSettings(root_dir=tmp_path / "site"),
        nginx=NginxSettings(),
        mita=MitaSettings(),
        trusttunnel=TrustTunnelSettings(install_dir=tmp_path / "tt"),
        hysteria=HysteriaSettings(install_dir=tmp_path / "hysteria"),
        mtproxyl=MTProxyLSettings(),
        yoomoney=YoomoneySettings(
            receiver="test-receiver",
            secret="test-secret",
            fee_percent=3.0,
        ),
        telegram_bot=TelegramBotSettings(
            token="123:ABC",
            username="test_bot",
            admin_username="admin",
        ),
        webhook=WebhookSettings(),
    )
