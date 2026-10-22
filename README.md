# vikavpn

Установка, харденинг сервера и доставка конфигурации.

## Hardening

Базовая защита сервера: root/user, SSH-ключи, порт, sshd_config, sysctl.

```bash
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sudo curl
curl -fsSL https://raw.githubusercontent.com/akril7/vikavpn/main/deploy/hardening.sh | sudo bash
```

## install

Установка/обновление приложения в `/opt/vikavpn` (venv, зависимости; конфиг в `/etc/vikavpn`).

```bash
curl -fsSL https://raw.githubusercontent.com/akril7/vikavpn/main/deploy/install.sh | sudo bash
```

## Push settings

Копирование локального **/etc/vikavpn/settings.env** на удалённый хост в **/etc/vikavpn/settings.env**.

```bash
curl -fsSL https://raw.githubusercontent.com/akril7/vikavpn/main/deploy/push-settings.sh | sudo bash
```
