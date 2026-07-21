# 修改 StackChan OTA URL

Xiaozhi-compatible 固件通常会从设备 NVS 里读取 OTA 地址。要让设备连接你的自建后端，需要把 OTA URL 改成你的公网 OTA 入口。

目标格式：

```text
https://<ota-domain.example.com>/xiaozhi/ota/
```

推荐流程：

1. 先确认你的 OTA 域名能访问宿主机的 `localhost:8003`。
2. 确认 WebSocket 域名能访问宿主机的 `localhost:8000`。
3. 用固件项目提供的 NVS/配置工具把设备里的 OTA URL 改成上面的地址。
4. 重启设备，看 Xiaozhi 后端日志里是否出现 OTA 请求和设备 ID。

如果你使用 `idf.py` 或固件仓库自带脚本，请以该固件文档为准。这个仓库只保存接入方法，不绑定某一个固件版本。

注意：`wakeup_words` 是服务端配置，不等于设备本地离线唤醒词。自定义唤醒词通常需要改固件里的唤醒模型。
