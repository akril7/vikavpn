#!/usr/bin/env bash
set -euo pipefail

# --------------------------------- PARAMS -----------------------------------------
ROOT_PASSWORD="${ROOT_PASSWORD:-}"
USER_NAME="${USER_NAME:-}"
USER_PASSWORD="${USER_PASSWORD:-}"
SSH_PORT="${SSH_PORT:-35790}"
PACKAGES=(sudo curl tree ca-certificates rsync python3 python3-venv python3-pip nginx dpkg git)
SSH_AUTHORIZED_KEYS=()
if [[ -n "${SSH_AUTHORIZED_KEYS_ENV:-}" ]]; then
    IFS=';' read -r -a SSH_AUTHORIZED_KEYS <<< "$SSH_AUTHORIZED_KEYS_ENV"
fi

# ------------------------------- READ PARAMS --------------------------------------

if [[ $EUID -ne 0 ]]; then
    echo "Please run as root" >&2
    exit 1
fi

if [[ -z "$ROOT_PASSWORD" ]]; then
    read -rs -p "New password for root: " ROOT_PASSWORD; echo
fi

if [[ -z "$USER_NAME" ]]; then
    read -r -p "Name of new user: " USER_NAME
fi

if [[ -z "$USER_PASSWORD" ]]; then
    read -rs -p "Password of new user: " USER_PASSWORD; echo
fi

if [[ ${#SSH_AUTHORIZED_KEYS[@]} -eq 0 ]]; then
    echo "Enter keys one by one (empty string - end)"
    while IFS= read -r -p "> " line; do
        [[ -z "$line" ]] && break
        SSH_AUTHORIZED_KEYS+=("$line")
    done
fi

if [[ ${#SSH_AUTHORIZED_KEYS[@]} -eq 0 ]]; then
    echo "No SSH keys provided — aborting" >&2
    exit 1
fi

# ------------------------------- HARDENING ----------------------------------------

# Change root password
echo "root:$ROOT_PASSWORD" | chpasswd

# Create new user (idempotent)
if id "$USER_NAME" &>/dev/null; then
    echo "User $USER_NAME already exists — skipping creation"
else
    useradd -m -U "$USER_NAME"
fi
echo "$USER_NAME:$USER_PASSWORD" | chpasswd

# Install packages
DEBIAN_FRONTEND=noninteractive apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${PACKAGES[@]}"

# Setup SSH keys for the new user
install -d -m 700 -o "$USER_NAME" -g "$USER_NAME" "/home/$USER_NAME/.ssh"
printf '%s\n' "${SSH_AUTHORIZED_KEYS[@]}" > "/home/$USER_NAME/.ssh/authorized_keys"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.ssh/authorized_keys"
chmod 600 "/home/$USER_NAME/.ssh/authorized_keys"

# Setup SSH keys for root
install -d -m 700 /root/.ssh
printf '%s\n' "${SSH_AUTHORIZED_KEYS[@]}" > /root/.ssh/authorized_keys
chown root:root /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# Setup sshd
cat > "/etc/ssh/sshd_config" <<EOF
Include /etc/ssh/sshd_config.d/*.conf

Port ${SSH_PORT}
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication yes
UsePAM yes

Subsystem sftp internal-sftp
EOF

sshd -t
systemctl reload ssh 2>/dev/null || systemctl reload sshd

# Setup SYSCTL
cat > "/etc/sysctl.d/90-vikavpn-tuning.conf" <<EOF
net.ipv4.tcp_keepalive_time=300
net.ipv4.tcp_keepalive_intvl=30
net.ipv4.tcp_keepalive_probes=3
net.ipv4.tcp_tw_reuse=1
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
net.core.netdev_max_backlog=65535
net.ipv4.tcp_fastopen=3
fs.file-max=2097152
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr

net.ipv4.tcp_fin_timeout=15
net.ipv4.tcp_syncookies=1
net.ipv4.tcp_sack=1
net.ipv4.tcp_dsack=1
net.ipv4.tcp_mtu_probing=1
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.core.rmem_default=131072
net.core.wmem_default=131072
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
net.ipv4.ip_forward=1
net.ipv6.conf.all.disable_ipv6=1
net.ipv6.conf.default.disable_ipv6=1
EOF

sysctl --system
