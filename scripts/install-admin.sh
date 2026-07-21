#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="${INSTALL_DIR:-/opt/stackchan-body-admin}"
SERVICE_USER="${SERVICE_USER:-$USER}"
SERVICE_GROUP="${SERVICE_GROUP:-$SERVICE_USER}"

sudo install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$INSTALL_DIR"
sudo install -m 0755 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$PROJECT_ROOT/admin/app.py" "$INSTALL_DIR/app.py"

if [[ ! -f "$INSTALL_DIR/admin.env" ]]; then
  sudo install -m 0600 -o "$SERVICE_USER" -g "$SERVICE_GROUP" "$PROJECT_ROOT/admin/admin.env.example" "$INSTALL_DIR/admin.env"
  echo "Created $INSTALL_DIR/admin.env. Edit it before starting the service."
fi

tmp_service="$(mktemp)"
sed "s/<linux-user>/$SERVICE_USER/g" "$PROJECT_ROOT/admin/systemd/stackchan-body-admin.service" > "$tmp_service"
sudo install -m 0644 "$tmp_service" /etc/systemd/system/stackchan-body-admin.service
rm -f "$tmp_service"

sudo systemctl daemon-reload
sudo systemctl enable stackchan-body-admin

echo "Installed. Next:"
echo "  sudo nano $INSTALL_DIR/admin.env"
echo "  sudo systemctl restart stackchan-body-admin"
