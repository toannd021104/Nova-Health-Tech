#!/bin/bash
# user_data runs as root on first boot of the EC2 instance.
# Installs Python 3.11+, Caddy, and prepares the app environment.
exec > /var/log/user-data.log 2>&1
set -x

dnf -y update
dnf -y install python3.11 python3.11-pip git tar gzip

# Install Caddy (ARM64)
CADDY_VER="2.10.0"
curl -L -o /tmp/caddy.tar.gz "https://github.com/caddyserver/caddy/releases/download/v${CADDY_VER}/caddy_${CADDY_VER}_linux_arm64.tar.gz"
tar xzf /tmp/caddy.tar.gz -C /usr/local/bin caddy
chmod +x /usr/local/bin/caddy

# Set default python symlink
ln -sf /usr/bin/python3.11 /usr/local/bin/python

# Give ec2-user ownership of /opt/nova
mkdir -p /opt/nova
chown ec2-user:ec2-user /opt/nova

touch /var/lib/cloud/instance/user-data-done
