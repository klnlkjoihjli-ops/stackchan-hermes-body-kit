#!/usr/bin/env bash
set -euo pipefail

# Load your provider keys. This file should define DEEPSEEK_API_KEY.
set -a
source "$HOME/.hermes/.env" 2>/dev/null || true
set +a

# Keep this body gateway isolated from your main Hermes gateway.
export API_SERVER_ENABLED=true
export API_SERVER_HOST=127.0.0.1
export API_SERVER_PORT=8643
export API_SERVER_MODEL_NAME=kengkeng-body
export API_SERVER_KEY="<your-body-api-server-key>"

# Avoid starting messaging platforms that may conflict with your main Hermes.
unset WEIXIN_ACCOUNT_ID WEIXIN_TOKEN WEIXIN_BASE_URL WEIXIN_CDN_BASE_URL
unset WEIXIN_DM_POLICY WEIXIN_ALLOW_ALL_USERS WEIXIN_ALLOWED_USERS
unset WEIXIN_GROUP_POLICY WEIXIN_GROUP_ALLOWED_USERS WEIXIN_HOME_CHANNEL
unset TELEGRAM_BOT_TOKEN TELEGRAM_ALLOWED_USERS TELEGRAM_ALLOWED_CHATS
unset FEISHU_APP_ID FEISHU_APP_SECRET FEISHU_BOT_NAME
unset LARK_APP_ID LARK_APP_SECRET LARK_APP_TOKEN LARK_VERIFICATION_TOKEN LARK_ENCRYPT_KEY

cd "$HOME/.hermes/hermes-agent"
exec "$HOME/.hermes/hermes-agent/venv/bin/python3" -m hermes_cli.main --profile kengkeng-body gateway run "$@"

