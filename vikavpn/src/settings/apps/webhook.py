from urllib.parse import urljoin

from pydantic_settings import BaseSettings

from src.settings.base import BaseSettingsConfigDict


class WebhookSettings(BaseSettings):
    model_config = BaseSettingsConfigDict(env_prefix="WEBHOOK_")

    urlpath: str = "/webhook"
    host: str = "127.0.0.1"
    port: int = 8081

    yoomoney_payment_urlpath: str = "/yoomoney/payment"
    hysteria_auth_urlpath: str = '/hysteria/auth'

    @property
    def hook_url(self):
        return urljoin(f"http://{self.host}:{self.port}", self.urlpath)

    @property
    def yoomoney_url(self):
        return self.hook_url + self.yoomoney_payment_urlpath

    @property
    def hysteria_url(self):
        return self.hook_url + self.hysteria_auth_urlpath
