#!/usr/bin/env bash
set -euo pipefail

# Example only. Replace placeholders before running.
TUNNEL_CONFIG="${TUNNEL_CONFIG:-$HOME/.cloudflared/stackchan-body.yml}"
OTA_DOMAIN="<ota-domain.example.com>"
WS_DOMAIN="<ws-domain.example.com>"
ADMIN_DOMAIN="<admin-domain.example.com>"

mkdir -p "$(dirname "$TUNNEL_CONFIG")"
cat > "$TUNNEL_CONFIG" <<YAML
tunnel: <your-cloudflare-tunnel-id>
credentials-file: /home/<linux-user>/.cloudflared/<your-cloudflare-tunnel-id>.json

ingress:
  - hostname: ${OTA_DOMAIN}
    service: http://127.0.0.1:8003
  - hostname: ${WS_DOMAIN}
    service: http://127.0.0.1:8000
  - hostname: ${ADMIN_DOMAIN}
    service: http://127.0.0.1:8787
  - service: http_status:404
YAML

echo "Wrote example config to $TUNNEL_CONFIG"
