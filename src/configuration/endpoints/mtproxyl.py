from pathlib import Path

from pydantic_settings import BaseSettings

from src.configuration.base import make_config


class MTProxyLSettings(BaseSettings):
    model_config = make_config(env_prefix="MTPROXYL_")

    # Путь до secrets.conf файла mtproxyl
    secrets_path: Path = Path("/opt/mtproxyl/secrets.conf")

    # URL для скачивание скрипта установки mtproxyl
    install_script_link: str = (
        "https://raw.githubusercontent.com/Liafanx/MTProxyL/main/install.sh"
    )

    # Имя службы
    service_name: str = "mtproxyl-telemt"

    # поддомен для веба (если пустой, используется domain из tls; использует сертификат из tls)
    subdomain: str = ""

    def build_domain(self, basedomain: str) -> str:
        if self.subdomain:
            return f"{self.subdomain.removesuffix('.')}.{basedomain}"
        return basedomain
