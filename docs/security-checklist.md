# 安全清单

这个项目的默认思路是：设备服务可以公网访问，管理面板和密钥不能裸奔。

上线前检查：

- 管理后台必须设置 `ADMIN_PASSWORD`。
- 管理后台只监听 `127.0.0.1`，由 Cloudflare Tunnel 或反向代理暴露。
- 管理后台前面建议再加 Cloudflare Access、Zero Trust、IP allowlist 或 VPN。
- Hermes body 的 `api_server.key` 使用长随机值，不要复用主 Hermes 的 key。
- Xiaozhi 后端开启设备白名单，只允许你的 `<device-mac>`。
- 不要把 Wi-Fi 密码、API key、真实域名、真实 IP、设备 MAC 提交进仓库。
- Cloudflare Tunnel 的 credentials JSON 权限设为仅服务用户可读。
- 日志里可能出现设备 ID、请求片段或错误详情，公开 issue 前先脱敏。
