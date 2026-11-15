from os import getenv as get
from datetime import timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
from uuid import UUID

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEFAULT_INSTALL_DIR = BASE_DIR / ".external"
DEFAULT_CONFIG_DIR = BASE_DIR
DOWNLOAD_DIR = Path("/tmp")

ENV_PATH = DEFAULT_CONFIG_DIR / "settings.env"


# --------- ENV ------------
load_dotenv(str(ENV_PATH))

DEBUG = get("DEBUG", "").lower() in ("yes", "true", "1")

TIMEZONE_HOURS_DELTA = int(get("TIMEZONE_HOURS_DELTA", "0"))
TZ = timezone(timedelta(hours=TIMEZONE_HOURS_DELTA))

DB_URL = get("DB_URL")

DEFAULT_USER = UUID(get("DEFAULT_USER", "0290e2fd8c244e19b7e7ab961ce6ea00")).hex
