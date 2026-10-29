#!/usr/bin/env bash
set -euo pipefail

# --------------------------------- PARAMS -----------------------------------------
# ENV-переменные (можно задать заранее для неинтерактивного запуска):
#   SETTINGS_SRC        — путь к локальному settings.env
#   CERT_DIR            — локальная папка с fullchain.pem и privkey.pem
#   SITE_DIR            — локальная папка с сайтом (index.html + подпапки)
#   REMOTE              — user@host
#   SSHPORT             — SSH-порт
#   REMOTE_SETTINGS     — путь settings.env на удалённой машине
#   REMOTE_CERT_DIR     — путь к папке с сертификатами на удалённой машине
#   REMOTE_SITE_DIR     — путь к папке сайта на удалённой машине
#   DOMAIN              — используется для пути сертификатов по умолчанию
SETTINGS_SRC="${SETTINGS_SRC:-}"
CERT_DIR="${CERT_DIR:-}"
SITE_DIR="${SITE_DIR:-}"
REMOTE="${REMOTE:-}"
SSHPORT="${SSHPORT:-}"
REMOTE_SETTINGS="${REMOTE_SETTINGS:-/etc/vikavpn/settings.env}"
REMOTE_CERT_DIR="${REMOTE_CERT_DIR:-}"
REMOTE_SITE_DIR="${REMOTE_SITE_DIR:-/opt/vikavpn/.external/site/}"
DOMAIN="${DOMAIN:-}"

# --------------------------------- UTILS ------------------------------------------
log() { printf '>>> %s\n' "$*"; }
die() { printf '!!! %s\n' "$*" >&2; exit 1; }

# ------------------------------- READ PARAMS --------------------------------------
# settings.env
if [[ -z "$SETTINGS_SRC" ]]; then
    read -r -p "Локальный settings.env: " SETTINGS_SRC
fi
[[ -n "$SETTINGS_SRC" ]] || die "SETTINGS_SRC не задан"

# папка с сертификатами
if [[ -z "$CERT_DIR" ]]; then
    read -r -p "Локальная папка с fullchain.pem и privkey.pem: " CERT_DIR
fi
[[ -n "$CERT_DIR" ]] || die "CERT_DIR не задан"

# папка с сайтом
if [[ -z "$SITE_DIR" ]]; then
    read -r -p "Локальная папка с сайтом (index.html + подпапки): " SITE_DIR
fi
[[ -n "$SITE_DIR" ]] || die "SITE_DIR не задан"

# удалённый хост
if [[ -z "$REMOTE" ]]; then
    read -r -p "Удалённый хост (user@host): " REMOTE
fi
[[ -n "$REMOTE" ]] || die "REMOTE не задан"

# порт SSH
if [[ -z "$SSHPORT" ]]; then
    read -r -p "SSH-порт [22]: " SSHPORT
    SSHPORT="${SSHPORT:-22}"
fi
[[ "$SSHPORT" =~ ^[0-9]+$ ]] || die "SSHPORT должен быть числом"

# домен (для пути сертификатов на удалённой машине по умолчанию)
if [[ -z "$DOMAIN" ]]; then
    DOMAIN="$(basename "$CERT_DIR")"
fi
if [[ -z "$REMOTE_CERT_DIR" ]]; then
    read -r -p "Путь к папке сертификатов на удалённой машине [/etc/letsencrypt/live/${DOMAIN}]: " REMOTE_CERT_DIR
    REMOTE_CERT_DIR="${REMOTE_CERT_DIR:-/etc/letsencrypt/live/${DOMAIN}}"
fi

# --------------------------------- CHECKS -----------------------------------------
[[ -f "$SETTINGS_SRC" ]]              || die "нет файла $SETTINGS_SRC"
[[ -f "$CERT_DIR/fullchain.pem" ]]    || die "нет файла $CERT_DIR/fullchain.pem"
[[ -f "$CERT_DIR/privkey.pem" ]]      || die "нет файла $CERT_DIR/privkey.pem"
[[ -d "$SITE_DIR" ]]                  || die "нет папки $SITE_DIR"
[[ -f "$SITE_DIR/index.html" ]]       || die "нет файла $SITE_DIR/index.html"

# ------------------------------- CREATE DIRS --------------------------------------
REMOTE_SETTINGS_DIR=$(dirname "$REMOTE_SETTINGS")
log "Создание каталога $REMOTE_SETTINGS_DIR на $REMOTE"
ssh -p "$SSHPORT" "$REMOTE" "install -d -m 750 '$REMOTE_SETTINGS_DIR'"

log "Создание каталога $REMOTE_CERT_DIR на $REMOTE"
ssh -p "$SSHPORT" "$REMOTE" "install -d -m 750 '$REMOTE_CERT_DIR'"

log "Создание каталога $REMOTE_SITE_DIR на $REMOTE"
ssh -p "$SSHPORT" "$REMOTE" "install -d -m 750 '$REMOTE_SITE_DIR'"

# --------------------------------- PUSH -------------------------------------------
log "Копирование $SETTINGS_SRC → $REMOTE:$REMOTE_SETTINGS"
scp -P "$SSHPORT" "$SETTINGS_SRC" "$REMOTE:$REMOTE_SETTINGS"

log "Копирование $CERT_DIR/fullchain.pem → $REMOTE:$REMOTE_CERT_DIR/fullchain.pem"
scp -P "$SSHPORT" "$CERT_DIR/fullchain.pem" "$REMOTE:$REMOTE_CERT_DIR/fullchain.pem"

log "Копирование $CERT_DIR/privkey.pem → $REMOTE:$REMOTE_CERT_DIR/privkey.pem"
scp -P "$SSHPORT" "$CERT_DIR/privkey.pem" "$REMOTE:$REMOTE_CERT_DIR/privkey.pem"

log "Копирование содержимого $SITE_DIR/ → $REMOTE:$REMOTE_SITE_DIR"
scp -P "$SSHPORT" -r "$SITE_DIR"/. "$REMOTE:$REMOTE_SITE_DIR"

# ------------------------------- PERMISSIONS --------------------------------------
log "Права на $REMOTE:$REMOTE_SETTINGS (600) и $REMOTE_CERT_DIR (600)"
ssh -p "$SSHPORT" "$REMOTE" "
    chmod 600 '$REMOTE_SETTINGS'
    chmod 600 '$REMOTE_CERT_DIR/fullchain.pem'
    chmod 600 '$REMOTE_CERT_DIR/privkey.pem'
    chmod -R a+rX '$REMOTE_SITE_DIR'
"

log "Готово: $REMOTE:$REMOTE_SETTINGS, $REMOTE:$REMOTE_CERT_DIR, $REMOTE:$REMOTE_SITE_DIR"
