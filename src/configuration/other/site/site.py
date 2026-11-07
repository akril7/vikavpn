from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.configuration.app import DEFAULT_INSTALL_DIR
from src.configuration.base import make_config


class SiteSettings(BaseSettings):
    model_config = make_config(env_prefix="SITE_")

    # Ссылка для архива с сайтом (внутри должен быть index.html)
    stub_download_url: str = ""

    # Ссылка для гайда
    guide_download_url: str = ""

    # абсолютный url-path до гайда
    guide_urlpath: Path = Field(default_factory=lambda: "files/guides/clashmi.mp4")

    # listen ssl port
    ssl_port: int = 7071

    # listen http port
    http_port: int = 7070

    # root папка сайта
    root_dir: Path = Field(default_factory=lambda: DEFAULT_INSTALL_DIR / "site")

    # имя файла для конфига сайта
    name: str = "vikavpn-site"
