import os

from pathlib import Path
from datetime import timezone, timedelta

from utils.systemctl import SystemdService

# Base
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
FILES_DIR = BASE_DIR / "files"

DEFAULT_INSTALL_DIR = BASE_DIR / "generated"

DEBUG = os.getenv("DEBUG").lower() in ("yes", "true", "1")
TIMEZONE_HOURS_DELTA = int(os.getenv("TIMEZONE_HOURS_DELTA"))
TZ = timezone(timedelta(hours=TIMEZONE_HOURS_DELTA))

# Domain setup
DOMAIN = os.getenv("DOMAIN")
CERT_PATH = Path(os.getenv("CERT_PATH"))
KEY_PATH = Path(os.getenv("KEY_PATH"))

# DB
DB_URL = os.getenv("DB_URL")

# Backends
SNI = os.getenv("SNI", "aeza.ru")

SERVICE_START_DELAY_SEC = 1

# Mita
MITA_PORT_RANGE = "10000-10127"
MITA_PROTOCOL = "UDP"
MITA_CONFIG_PATH = Path(os.getenv("MITA_CONFIG_PATH") or (DEFAULT_INSTALL_DIR / "mieru" / "mita.json"))
MITA_SERVICE = SystemdService("mita")
MITA_PACKAGE_DOWNLOAD_LINK = "https://github.com/enfein/mieru/releases/download/v3.36.1/mita_3.36.1_amd64.deb"

# Hysteria
HYSTERIA_PORT = 11443
HYSTERIA_CONFIG_PATH = Path(os.getenv("HYSTERIA_CONFIG_PATH") or (DEFAULT_INSTALL_DIR / "hysteria" / "hysteria.yaml"))
HYSTERIA_DOCKER_IMAGE_NAME = "teddysun/hysteria"
HYSTERIA_DOCKER_CONTAINER_NAME = "hysteria"

# Trusttunnel
TRUSTTUNNEL_PORT = 8443
TRUSTTUNNEL_INSTALL_DIR = Path(os.getenv("TRUSTTUNNEL_INSTALL_DIR") or (DEFAULT_INSTALL_DIR / "trusttunnel"))
TRUSTTUNNEL_SERVICE = SystemdService("trusttunnel")
TRUSTTUNNEL_ARCHIVE_DOWNLOAD_LINK = "https://github.com/TrustTunnel/TrustTunnel/releases/download/v1.1.0/trusttunnel-v1.1.0-linux-x86_64.tar.gz"
TRUSTTUNNEL_ARCHIVE_NAME = os.path.basename(TRUSTTUNNEL_ARCHIVE_DOWNLOAD_LINK)

# MTProxyL
MTPROXYL_PORT = 7443
MTPROXYL_DEFAULT_USER = "default"
MTPROXYL_DEFAULT_USER_UUID = "c97a7565cf5146b63d8e31f8f95da840"
MTPROXYL_SECRETS_PATH = Path("/opt/mtproxyl/secrets.conf")
MTPROXYL_INSTALL_SCRIPT_LINK = "https://raw.githubusercontent.com/Liafanx/MTProxyL/main/install.sh"
MTPROXYL_MODE = "manager"
MTPROXYL_USE_ZAPRET2 = True

# Clash
CLASH_CONFIGS_STORE_DIR = DEFAULT_INSTALL_DIR / "clash" / "configs"

# Web server
WEBSERVER_TITLE = "VIKA-WASSUP"
WEBSERVER_PORT = 443
WEBSERVER_ROOT = DEFAULT_INSTALL_DIR / "webserver"
WEBSERVER_NGINX_AVAILABLE_PATH = Path("/etc/nginx/sites-available/vikavpn-webserver")
WEBSERVER_NGINX_ENABLED_PATH = Path("/etc/nginx/sites-enabled/vikavpn-webserver")
NGINX_SERVICE = SystemdService("nginx")
