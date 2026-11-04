from pathlib import Path

from pydantic_settings import BaseSettings

from src.settings.base import make_config


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

    # Путь до папки с сайтом (stub - использовать встроенный)
    selfmask_template: str = "stub"

    # socks5 адрес для upstream (если не указан, используется direct)
    socks5_upstream_address: str = ""

    # поддомен для веба (если пустой, используется domain из tls; использует сертификат из tls)
    subdomain: str = ""
