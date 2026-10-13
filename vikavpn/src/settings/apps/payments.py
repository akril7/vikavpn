from pydantic_settings import BaseSettings

from src.settings.base import make_config


class PaymentsSettings(BaseSettings):
    model_config = make_config(env_prefix="PAYMENTS_")

    # адрес, который слушает приложение
    host: str = "127.0.0.1"
    port: int = 11082

    # путь, по которому принимаем вебхук ЮMoney
    payment_path: str = "/payments/yoomoney"

    # таймаут HTTP-запроса к reload
    reload_timeout: float = 5.0

    @property
    def origin(self) -> str:
        return f"http://{self.host}:{self.port}"
