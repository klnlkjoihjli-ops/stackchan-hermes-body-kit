#!/usr/bin/env python3
import base64
import datetime as dt
import json
import os
import secrets
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = os.getenv("ADMIN_HOST", "127.0.0.1")
PORT = int(os.getenv("ADMIN_PORT", "8787"))
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

XIAOZHI_DIR = Path(os.getenv("XIAOZHI_DIR", "/opt/xiaozhi-esp32-server"))
XIAOZHI_CONFIG = Path(os.getenv("XIAOZHI_CONFIG", str(XIAOZHI_DIR / "data/.config.yaml")))
XIAOZHI_CONTAINER = os.getenv("XIAOZHI_CONTAINER", "xiaozhi-esp32-server")
XIAOZHI_COMPOSE_SERVICE = os.getenv("XIAOZHI_COMPOSE_SERVICE", XIAOZHI_CONTAINER)

BODY_PROFILE = Path(os.getenv("BODY_PROFILE", str(Path.home() / ".hermes/profiles/kengkeng-body")))
BODY_PREFILL = Path(os.getenv("BODY_PREFILL", str(BODY_PROFILE / "prefill.json")))
BODY_USER_SERVICE = os.getenv("BODY_USER_SERVICE", "kengkeng-body")
BODY_API_HOST = os.getenv("BODY_API_HOST", "127.0.0.1")
BODY_API_PORT = int(os.getenv("BODY_API_PORT", "8643"))
USER_SYSTEMD_UID = os.getenv("USER_SYSTEMD_UID", str(os.getuid()))

CLOUDFLARED_SERVICE = os.getenv("CLOUDFLARED_SERVICE", "cloudflared")
OTA_HEALTH_URL = os.getenv("OTA_HEALTH_URL", "http://127.0.0.1:8003/xiaozhi/ota/")
ADMIN_TITLE = os.getenv("ADMIN_TITLE", "StackChan Body Admin")
PUBLIC_LABEL = os.getenv("PUBLIC_LABEL", "local")


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>StackChan Body Admin</title>
  <style>
    :root { color-scheme: light dark; --bg:#f6f7f9; --panel:#fff; --text:#15171a; --muted:#667085; --line:#d9dee7; --ok:#16824a; --warn:#b45309; --bad:#b42318; --accent:#1455d9; }
    @media (prefers-color-scheme: dark) { :root { --bg:#111315; --panel:#191c20; --text:#ecf0f5; --muted:#9aa4b2; --line:#2d333b; } }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }
    header { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:18px 24px; border-bottom:1px solid var(--line); background:var(--panel); position:sticky; top:0; z-index:2; }
    h1 { font-size:20px; margin:0; }
    .sub { color:var(--muted); font-size:13px; margin-top:4px; }
    main { max-width:1280px; margin:0 auto; padding:20px 24px 36px; display:grid; grid-template-columns:360px minmax(0,1fr); gap:20px; }
    section { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; }
    h2 { font-size:15px; margin:0 0 12px; }
    .stack,.grid { display:grid; gap:20px; }
    .grid { gap:10px; }
    .row { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:9px 0; border-bottom:1px solid var(--line); font-size:14px; }
    .row:last-child { border-bottom:0; }
    .label { color:var(--muted); }
    .pill { border-radius:999px; padding:3px 8px; font-size:12px; border:1px solid var(--line); white-space:nowrap; max-width:210px; overflow:hidden; text-overflow:ellipsis; }
    .ok { color:var(--ok); }
    .warn { color:var(--warn); }
    .bad { color:var(--bad); }
    .controls { display:flex; flex-wrap:wrap; gap:8px; }
    button,select { border:1px solid var(--line); border-radius:6px; background:var(--panel); color:var(--text); padding:8px 10px; font:inherit; font-size:13px; }
    button.primary { background:var(--accent); border-color:var(--accent); color:white; }
    textarea { width:100%; min-height:320px; resize:vertical; border:1px solid var(--line); border-radius:8px; padding:12px; background:var(--panel); color:var(--text); font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
    pre { margin:0; padding:12px; min-height:420px; max-height:680px; overflow:auto; border:1px solid var(--line); border-radius:8px; background:#0f1720; color:#d9e3f0; font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; white-space:pre-wrap; }
    .toast { min-height:20px; color:var(--muted); font-size:13px; }
    @media (max-width:900px) { main { grid-template-columns:1fr; padding:14px; } header { padding:14px; align-items:flex-start; } }
  </style>
</head>
<body>
  <header>
    <div>
      <h1 id="title">StackChan Body Admin</h1>
      <div id="label" class="sub">local</div>
    </div>
    <div class="controls">
      <button onclick="refreshAll()">刷新</button>
      <button class="primary" onclick="savePrompt()">保存提示词</button>
    </div>
  </header>
  <main>
    <div class="stack">
      <section>
        <h2>状态</h2>
        <div id="status" class="grid"></div>
      </section>
      <section>
        <h2>动作</h2>
        <div class="controls">
          <button onclick="action('restart_body')">重启分身</button>
          <button onclick="action('restart_xiaozhi')">重启 Xiaozhi</button>
          <button onclick="action('restart_cloudflared')">重启 Tunnel</button>
        </div>
        <p id="toast" class="toast"></p>
      </section>
      <section>
        <h2>日志</h2>
        <div class="controls">
          <select id="logTarget" onchange="loadLogs()">
            <option value="xiaozhi">Xiaozhi</option>
            <option value="body">Hermes body</option>
            <option value="cloudflared">Cloudflared</option>
          </select>
          <button onclick="loadLogs()">刷新日志</button>
        </div>
      </section>
    </div>
    <div class="stack">
      <section>
        <h2>提示词</h2>
        <textarea id="prompt"></textarea>
      </section>
      <section>
        <h2>实时日志</h2>
        <pre id="logs">加载中...</pre>
      </section>
    </div>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    function cls(value) {
      const s = String(value || '').toLowerCase();
      if (s.includes('active') || s.includes('up') || s.includes('200') || s === 'ok' || s.includes('listening')) return 'ok';
      if (s.includes('fail') || s.includes('error') || s.includes('down') || s.includes('inactive') || s.includes('not ')) return 'bad';
      return 'warn';
    }
    async function api(path, options) {
      const res = await fetch(path, options);
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }
    async function refreshStatus() {
      const data = await api('/api/status');
      $('title').textContent = data.title;
      $('label').textContent = data.label;
      $('status').innerHTML = data.items.map(item => `
        <div class="row">
          <span class="label">${item.label}</span>
          <span class="pill ${cls(item.value)}" title="${item.value}">${item.value}</span>
        </div>`).join('');
    }
    async function loadConfig() {
      const data = await api('/api/config');
      $('prompt').value = data.prompt || '';
    }
    async function savePrompt() {
      $('toast').textContent = '保存中...';
      const data = await api('/api/config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: $('prompt').value})
      });
      $('toast').textContent = data.message;
      await loadLogs();
    }
    async function loadLogs() {
      const target = $('logTarget').value;
      const text = await fetch(`/api/logs?target=${encodeURIComponent(target)}&lines=180`).then(r => r.text());
      $('logs').textContent = text;
    }
    async function action(name) {
      if (!confirm('确认执行这个动作？')) return;
      $('toast').textContent = '执行中...';
      const data = await api('/api/action', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: name})
      });
      $('toast').textContent = data.message;
      setTimeout(refreshAll, 1500);
    }
    async function refreshAll() {
      await Promise.allSettled([refreshStatus(), loadConfig(), loadLogs()]);
    }
    refreshAll();
    setInterval(refreshStatus, 10000);
  </script>
</body>
</html>
"""


def run_cmd(command: str, timeout: int = 15) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return completed.returncode, completed.stdout.strip()
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return 124, (output.strip() + "\nTimed out").strip()


def status_value(command: str, fallback: str = "unknown") -> str:
    code, out = run_cmd(command, timeout=8)
    if code != 0 and not out:
        return fallback
    return out.splitlines()[0].strip() if out else fallback


def read_body_prompt() -> str:
    try:
        data = json.loads(BODY_PREFILL.read_text())
        if isinstance(data, list):
            for msg in data:
                if msg.get("role") == "system":
                    return str(msg.get("content", ""))
    except Exception:
        pass
    return ""


def write_body_prompt(prompt: str) -> None:
    BODY_PROFILE.mkdir(parents=True, exist_ok=True)
    BODY_PREFILL.write_text(
        json.dumps([{"role": "system", "content": prompt}], ensure_ascii=False, indent=2) + "\n"
    )


def replace_yaml_prompt(text: str, prompt: str) -> str:
    lines = text.splitlines()
    out = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        if line.startswith("prompt:"):
            out.append("prompt: |")
            for prompt_line in prompt.splitlines():
                out.append("  " + prompt_line)
            replaced = True
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                i += 1
            continue
        out.append(line)
        i += 1
    if not replaced:
        out.extend(["", "prompt: |"])
        out.extend("  " + line for line in prompt.splitlines())
    return "\n".join(out) + "\n"


def write_xiaozhi_prompt(prompt: str) -> None:
    if not XIAOZHI_CONFIG.exists():
        return
    text = XIAOZHI_CONFIG.read_text()
    backup = XIAOZHI_CONFIG.with_suffix(".yaml.bak-" + dt.datetime.now().strftime("%Y%m%d%H%M%S"))
    backup.write_text(text)
    XIAOZHI_CONFIG.write_text(replace_yaml_prompt(text, prompt))


def json_response(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    server_version = "StackChanBodyAdmin/0.1"

    def _authorized(self) -> bool:
        if not ADMIN_PASSWORD:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
        except Exception:
            return False
        user, _, password = decoded.partition(":")
        return secrets.compare_digest(user, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASSWORD)

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="StackChan Body Admin", charset="UTF-8"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_GET(self) -> None:
        if not self._require_auth():
            return
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            data = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/api/status":
            self.handle_status()
            return
        if parsed.path == "/api/config":
            json_response(self, {"prompt": read_body_prompt()})
            return
        if parsed.path == "/api/logs":
            self.handle_logs(parsed.query)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if not self._require_auth():
            return
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            json_response(self, {"error": "invalid json"}, 400)
            return
        if parsed.path == "/api/config":
            prompt = str(payload.get("prompt", "")).strip()
            if not prompt:
                json_response(self, {"error": "prompt is required"}, 400)
                return
            write_body_prompt(prompt)
            write_xiaozhi_prompt(prompt)
            json_response(self, {"message": "提示词已保存；重启分身和 Xiaozhi 后生效"})
            return
        if parsed.path == "/api/action":
            self.handle_action(str(payload.get("action", "")))
            return
        self.send_error(404)

    def handle_status(self) -> None:
        xiaozhi = status_value(
            f'sudo -n /usr/bin/docker ps --filter name={XIAOZHI_CONTAINER} --format "{{{{.Status}}}}" | head -n1',
            "not running",
        )
        body = status_value(
            f"XDG_RUNTIME_DIR=/run/user/{USER_SYSTEMD_UID} systemctl --user is-active {BODY_USER_SERVICE}",
            "unknown",
        )
        tunnel = status_value(f"systemctl is-active {CLOUDFLARED_SERVICE}", "unknown")
        ota_code = status_value(
            f"curl -sS -o /dev/null -w '%{{http_code}}' --max-time 5 {OTA_HEALTH_URL}",
            "000",
        )
        body_code = status_value(
            f"ss -ltn | awk '$4 ~ /{BODY_API_HOST}:{BODY_API_PORT}$/ {{print \"listening\"; exit}}'",
            "not listening",
        )
        last_device = status_value(
            f"sudo -n /usr/bin/docker logs --tail=220 {XIAOZHI_CONTAINER} 2>&1 | grep -E 'OTA|conn|识别文本|ASR|LLM|TTS|error|Error' | tail -n1",
            "no recent device log",
        )
        json_response(
            self,
            {
                "title": ADMIN_TITLE,
                "label": PUBLIC_LABEL,
                "items": [
                    {"label": "Xiaozhi 容器", "value": xiaozhi},
                    {"label": "Hermes body", "value": body},
                    {"label": "Cloudflare Tunnel", "value": tunnel},
                    {"label": "OTA 本地接口", "value": ota_code},
                    {"label": "分身 API", "value": body_code or "not listening"},
                    {"label": "最近设备事件", "value": last_device[-96:]},
                ],
            },
        )

    def handle_logs(self, query: str) -> None:
        params = urllib.parse.parse_qs(query)
        target = params.get("target", ["xiaozhi"])[0]
        try:
            lines = max(20, min(500, int(params.get("lines", ["180"])[0])))
        except ValueError:
            lines = 180
        commands = {
            "xiaozhi": f"sudo -n /usr/bin/docker logs --tail={lines} {XIAOZHI_CONTAINER} 2>&1",
            "body": f"XDG_RUNTIME_DIR=/run/user/{USER_SYSTEMD_UID} journalctl --user -u {BODY_USER_SERVICE} -n {lines} --no-pager 2>&1",
            "cloudflared": f"journalctl -u {CLOUDFLARED_SERVICE} -n {lines} --no-pager 2>&1",
        }
        command = commands.get(target)
        if not command:
            self.send_error(400, "unknown target")
            return
        _, out = run_cmd(command, timeout=20)
        data = out.encode("utf-8", errors="replace")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_action(self, action: str) -> None:
        commands = {
            "restart_body": f"XDG_RUNTIME_DIR=/run/user/{USER_SYSTEMD_UID} systemctl --user restart {BODY_USER_SERVICE}",
            "restart_xiaozhi": f"cd {XIAOZHI_DIR} && sudo -n /usr/bin/docker compose restart {XIAOZHI_COMPOSE_SERVICE}",
            "restart_cloudflared": f"sudo -n /usr/bin/systemctl restart {CLOUDFLARED_SERVICE}",
        }
        command = commands.get(action)
        if not command:
            json_response(self, {"error": "unknown action"}, 400)
            return
        code, out = run_cmd(command, timeout=30)
        if code != 0:
            json_response(self, {"error": out or "action failed"}, 500)
            return
        json_response(self, {"message": "动作已执行"})

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    if not ADMIN_PASSWORD:
        print("WARNING: ADMIN_PASSWORD is empty; authentication disabled")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"StackChan Body Admin listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
