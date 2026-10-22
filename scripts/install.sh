#!/usr/bin/env bash
set -euo pipefail

# --------------------------------- PARAMS -----------------------------------------
REPO_URL="${REPO_URL:-https://github.com/USER/vikavpn.git}"
TARGET="${TARGET:-/opt/vikavpn}"
BRANCH="${BRANCH:-main}"
CONF_DIR="${CONF_DIR:-/etc/vikavpn}"
VENV_DIR="${VENV_DIR:-$TARGET/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# --------------------------------- UTILS ------------------------------------------
log()  { printf '>>> %s\n' "$*"; }
die()  { printf '!!! %s\n' "$*" >&2; exit 1; }

# --------------------------------- CHECKS -----------------------------------------
[[ $EUID -eq 0 ]] || die "Запустите через sudo (нужен root для /opt и /etc)"
command -v git >/dev/null || die "git не установлен"
command -v "$PYTHON_BIN" >/dev/null || die "$PYTHON_BIN не установлен"

# --------------------------- CLONE / UPDATE ---------------------------------------
if [[ -d "$TARGET/.git" ]]; then
    log "Обновление $TARGET (ветка $BRANCH)"
    git -C "$TARGET" fetch --prune origin
    git -C "$TARGET" checkout "$BRANCH"
    git -C "$TARGET" reset --hard "origin/$BRANCH"
    git -C "$TARGET" clean -fdx -e .venv
else
    log "Клонирование $REPO_URL → $TARGET"
    rm -rf "$TARGET"
    git clone --branch "$BRANCH" "$REPO_URL" "$TARGET"
fi

# --------------------------------- CONFIG -----------------------------------------
log "Каталог конфигурации: $CONF_DIR"
mkdir -p "$CONF_DIR"
chmod 750 "$CONF_DIR"

if [[ -f "$TARGET/.env.example" && ! -f "$CONF_DIR/.env" ]]; then
    cp "$TARGET/.env.example" "$CONF_DIR/.env"
    chmod 600 "$CONF_DIR/.env"
    log "Создан $CONF_DIR/.env из .env.example — отредактируйте его"
elif [[ ! -f "$CONF_DIR/.env" ]]; then
    log "ВНИМАНИЕ: $CONF_DIR/.env отсутствует, а .env.example в репозитории нет"
fi

# --------------------------------- VENV -------------------------------------------
if [[ ! -f "$TARGET/requirements.txt" ]]; then
    log "requirements.txt не найден — пропускаю настройку venv"
else
    # создаём venv, если его нет
    if [[ ! -x "$VENV_DIR/bin/python" ]]; then
        log "Создание venv: $VENV_DIR"
        "$PYTHON_BIN" -m venv "$VENV_DIR"
    else
        log "venv уже существует: $VENV_DIR"
    fi

    # обновляем pip и ставим зависимости
    log "Обновление pip"
    "$VENV_DIR/bin/python" -m pip install --upgrade pip -q

    log "Установка зависимостей из requirements.txt"
    "$VENV_DIR/bin/pip" install -r "$TARGET/requirements.txt" -q

    log "Зависимости установлены: $("$VENV_DIR/bin/python" --version 2>&1)"
fi

# --------------------------------- VERSION ----------------------------------------
HASH=$(git -C "$TARGET" rev-parse --short HEAD)
BRANCH_NOW=$(git -C "$TARGET" rev-parse --abbrev-ref HEAD)
DESC=$(git -C "$TARGET" describe --tags --always --dirty 2>/dev/null || echo "$HASH")

log "Установлено: $HASH (branch=$BRANCH_NOW, desc=$DESC)"
log "Готово."
