#!/usr/bin/env bash
set -euo pipefail

# --------------------------------- PARAMS -----------------------------------------
SRC="${SRC:-}"
REMOTE="${REMOTE:-}"
SSHPORT="${SSHPORT:-}"
DEST="${DEST:-/etc/vikavpn/settings.env}"

# --------------------------------- UTILS ------------------------------------------
log() { printf '>>> %s\n' "$*"; }
die() { printf '!!! %s\n' "$*" >&2; exit 1; }

# ------------------------------- READ PARAMS --------------------------------------
if [[ -z "$SRC" ]]; then
    read -r -p "Локальный файл [settings.env]: " SRC
    SRC="${SRC:-/etc/vikavpn/settings.env}"
fi

if [[ -z "$REMOTE" ]]; then
    read -r -p "Удалённый хост (user@host): " REMOTE
fi

if [[ -z "$SSHPORT" ]]; then
    read -r -p "SSH-порт [22]: " SSHPORT
    SSHPORT="${SSHPORT:-22}"
fi

# --------------------------------- CHECKS -----------------------------------------
[[ -n "$REMOTE" ]] || die "REMOTE не задан"
[[ -f "$SRC" ]]    || die "нет файла $SRC"
[[ "$SSHPORT" =~ ^[0-9]+$ ]] || die "SSHPORT должен быть числом"

# ------------------------------- CREATE DIR ---------------------------------------
DEST_DIR=$(dirname "$DEST")
log "Создание каталога $DEST_DIR на $REMOTE"
ssh -p "$SSHPORT" "$REMOTE" "install -d -m 750 '$DEST_DIR'"

# --------------------------------- PUSH -------------------------------------------
log "Копирование $SRC → $REMOTE:$DEST"
scp -P "$SSHPORT" "$SRC" "$REMOTE:$DEST"

# ------------------------------- PERMISSIONS --------------------------------------
log "Права 600 на $REMOTE:$DEST"
ssh -p "$SSHPORT" "$REMOTE" "chmod 600 '$DEST'"

log "Готово: $REMOTE:$DEST"
