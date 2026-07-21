#!/usr/bin/env python3
import argparse
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch Xiaozhi config to use a Hermes OpenAI-compatible endpoint.")
    parser.add_argument("config", type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--model", default="kengkeng-body")
    parser.add_argument("--device-mac", action="append", default=[])
    args = parser.parse_args()

    data = yaml.safe_load(args.config.read_text()) or {}
    data.setdefault("selected_module", {})["LLM"] = "HermesLLM"
    data.setdefault("LLM", {})["HermesLLM"] = {
        "type": "openai",
        "model_name": args.model,
        "base_url": args.base_url,
        "api_key": args.api_key,
        "timeout": {"connect": 3.0, "read": 180.0, "write": 10.0, "pool": 2.0},
    }
    if args.device_mac:
        server = data.setdefault("server", {})
        auth = server.setdefault("auth", {})
        auth["enabled"] = True
        auth["allowed_devices"] = args.device_mac

    backup = args.config.with_suffix(args.config.suffix + ".bak")
    backup.write_text(args.config.read_text())
    args.config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
    print(f"Patched {args.config}; backup saved to {backup}")


if __name__ == "__main__":
    main()
