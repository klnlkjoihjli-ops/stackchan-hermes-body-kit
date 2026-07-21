# 排障

## 设备说“忙，稍后再试”

这通常说明设备链路已经通了：麦克风、ASR 或 TTS 至少有一部分可用。最常见失败点是 Xiaozhi 后端调用 LLM 失败。

检查顺序：

```bash
sudo docker logs --tail=200 xiaozhi-esp32-server
```

重点看 `LLM`、`api_key`、`base_url`、`timeout`、`Connection refused`、`401`、`404`。

## Docker 里访问不到 Hermes

如果 Hermes body 监听 `127.0.0.1:8643`，Docker bridge 网络里的 Xiaozhi 容器访问自己的 `127.0.0.1`，不是访问宿主机。

推荐做法：

```yaml
network_mode: host
```

或者把 Hermes API 绑定到容器能访问的内网地址，并做好防火墙限制。

## Cloudflare 返回 1033

这表示 Cloudflare 没有连到你的 tunnel。

检查：

```bash
systemctl status cloudflared
journalctl -u cloudflared -n 100 --no-pager
```

如果机器上有多个 tunnel 服务，要确认你改的是正在运行的那个服务配置。

## OTA 可以访问，但设备不进 WebSocket

建议 OTA 和 WebSocket 拆成两个 hostname：

```text
<ota-domain.example.com> -> localhost:8003
<ws-domain.example.com>  -> localhost:8000
```

单域名 path 分流在某些配置下容易出现 404 或 WebSocket upgrade 没转发。

## 测试 Hermes body

```bash
KEY="<your-body-api-server-key>"

curl -sS http://127.0.0.1:8643/v1/models \
  -H "Authorization: Bearer $KEY"

curl -N -sS http://127.0.0.1:8643/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kengkeng-body","messages":[{"role":"user","content":"嗨，你在吗"}],"stream":true}'
```
