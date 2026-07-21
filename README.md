# StackChan Hermes Body Kit

把 M5Stack StackChan / CoreS3 变成自建 Hermes 智能体身体的一套模板工程。

这个仓库不包含任何真实域名、IP、MAC、账号、密码或 API key。它只保留接入方法、配置模板、管理后台和排障流程。

## 架构

```text
StackChan
  -> 自建 Xiaozhi-compatible 后端
  -> Hermes 轻量身体分身
  -> 你的模型供应商，例如 DeepSeek
```

推荐公网入口：

```text
https://<ota-domain>/xiaozhi/ota/      -> Xiaozhi HTTP/OTA, localhost:8003
wss://<ws-domain>/xiaozhi/v1/          -> Xiaozhi WebSocket, localhost:8000
https://<admin-domain>/                -> 管理后台, localhost:8787
```

## 适合什么场景

- 你已经有 StackChan / CoreS3。
- 你想刷 Xiaozhi-compatible 固件，但不想只用官方后台。
- 你想让设备接入自己的 Hermes / Codex / agent 服务。
- 你希望语音对话走轻量分身，而不是每句话都启动完整工作大脑。

## 目录

```text
admin/                         管理后台
examples/                      Hermes、Xiaozhi、Cloudflare 配置模板
scripts/                       部署和配置辅助脚本
docs/                          NVS、排障、安全说明
```

## 快速部署

以下命令在你的 Ubuntu 机器上执行。

如果要使用 `scripts/patch-xiaozhi-config.py`，先安装脚本依赖：

```bash
python3 -m pip install -r requirements.txt
```

1. 准备 Hermes 身体分身

```bash
mkdir -p ~/.hermes/profiles/kengkeng-body ~/scripts
cp examples/hermes-kengkeng-body.config.yaml ~/.hermes/profiles/kengkeng-body/config.yaml
cp examples/prefill.json ~/.hermes/profiles/kengkeng-body/prefill.json
cp examples/start-kengkeng-body.sh ~/scripts/start-kengkeng-body.sh
chmod +x ~/scripts/start-kengkeng-body.sh
```

编辑：

```bash
nano ~/.hermes/profiles/kengkeng-body/config.yaml
nano ~/scripts/start-kengkeng-body.sh
```

把占位符替换为你自己的 API key、端口和模型。

2. 启动 Hermes 身体分身

```bash
mkdir -p ~/.config/systemd/user
cp examples/kengkeng-body.service ~/.config/systemd/user/kengkeng-body.service
systemctl --user daemon-reload
systemctl --user enable --now kengkeng-body
```

验证：

```bash
KEY="<your-body-api-server-key>"

curl -sS http://127.0.0.1:8643/v1/models \
  -H "Authorization: Bearer $KEY"

curl -N -sS http://127.0.0.1:8643/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"kengkeng-body","messages":[{"role":"user","content":"嗨，你在吗"}],"stream":true}'
```

3. 部署 Xiaozhi-compatible 后端

参考 `examples/xiaozhi.config.example.yaml`。关键是：

```yaml
LLM:
  HermesLLM:
    type: openai
    model_name: "kengkeng-body"
    base_url: http://127.0.0.1:8643/v1/
    api_key: "<your-body-api-server-key>"
```

如果 Xiaozhi 用 Docker 运行，而 Hermes 只监听宿主机 `127.0.0.1`，推荐让 Xiaozhi 容器使用 host network，或者把 Hermes API 绑定到容器可访问的安全内网地址。

4. 配置 Cloudflare Tunnel

参考 `examples/cloudflared-ingress.example.yml`。

建议拆成两个 hostname：

```text
<ota-domain> -> localhost:8003
<ws-domain>  -> localhost:8000
```

这样比单域名 path 分流更稳。

5. 修改 StackChan OTA URL

参考 [docs/nvs-ota-url.md](docs/nvs-ota-url.md)。

目标 OTA URL：

```text
https://<ota-domain>/xiaozhi/ota/
```

## 管理后台

后台是一个无数据库的 Python 小服务，适合内网/Cloudflare Tunnel 后面的运维控制台。

功能：

- 查看 Xiaozhi、Hermes body、Cloudflare Tunnel 状态
- 查看日志
- 编辑身体分身提示词
- 重启相关服务

部署：

```bash
sudo scripts/install-admin.sh
```

编辑：

```bash
sudo nano /opt/stackchan-body-admin/admin.env
sudo systemctl restart stackchan-body-admin
```

默认监听：

```text
127.0.0.1:8787
```

## 重要限制

服务端 `wakeup_words` 不能直接替换设备离线唤醒词模型。真正把唤醒词改成自定义词，需要修改/训练/替换固件里的唤醒词模型。

## 排障

看 [docs/troubleshooting.md](docs/troubleshooting.md)。

最常见的一句话：

```text
主人，小智现在有点忙，我们稍后再试吧
```

这通常说明设备、ASR、TTS 已经通了，失败点在 LLM 连接或模型 provider。
