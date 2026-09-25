from os import getenv as get
from datetime import timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = BASE_DIR / "files"

DEFAULT_INSTALL_DIR = BASE_DIR / "external"

DEBUG = get("DEBUG", "").lower() in ("yes", "true", "1")

TIMEZONE_HOURS_DELTA = int(get("TIMEZONE_HOURS_DELTA", "0"))
TZ = timezone(timedelta(hours=TIMEZONE_HOURS_DELTA))

SNI = get("SNI", "aeza.ru")

DB_URL = get("DB_URL")
