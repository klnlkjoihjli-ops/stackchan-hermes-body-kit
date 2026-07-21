# Security

This repository is a template. Never commit real values for:

- domain administration tokens
- Cloudflare tunnel credentials
- Wi-Fi SSID/password
- Xiaozhi API keys
- Hermes `API_SERVER_KEY`
- upstream provider keys such as `DEEPSEEK_API_KEY`
- device MAC addresses when you do not want them public

Recommended deployment shape:

- Keep Hermes API bound to `127.0.0.1`.
- Expose only Xiaozhi OTA/WS and the admin panel through Cloudflare Tunnel.
- Protect the admin panel with Basic Auth or Cloudflare Access.
- Use `sudoers` allowlists for the admin panel; do not grant unrestricted sudo.

