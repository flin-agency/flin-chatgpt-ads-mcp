#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
INSTALL_DIR="${FLIN_ADS_INSTALL_DIR:-$HOME/.local/share/flin-chatgpt-ads-mcp}"
CONFIG_DIR="${FLIN_ADS_CONFIG_DIR:-$HOME/.config/flin-chatgpt-ads-mcp}"
if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
elif [ -x "$HOME/.local/bin/uv" ]; then
  UV_BIN="$HOME/.local/bin/uv"
else
  UV_BIN=""
fi
mkdir -p "$INSTALL_DIR" "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"
if [ -n "$UV_BIN" ]; then
  if [ ! -x "$INSTALL_DIR/venv/bin/python" ]; then
    "$UV_BIN" venv --python 3.12 "$INSTALL_DIR/venv"
  fi
  "$UV_BIN" pip install --python "$INSTALL_DIR/venv/bin/python" --upgrade ./flin_chatgpt_ads_mcp-*.whl
else
  if ! python3 -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
    echo 'Bitte Python 3.11+ oder uv installieren und dieses Programm erneut öffnen.' >&2
    exit 1
  fi
  if [ ! -x "$INSTALL_DIR/venv/bin/python" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
  fi
  "$INSTALL_DIR/venv/bin/python" -m pip install --upgrade ./flin_chatgpt_ads_mcp-*.whl
fi
if [ ! -e "$CONFIG_DIR/config.json" ]; then
  (umask 077; printf '%s\n' '{"accounts": {"mein_konto": {"api_key": "HIER_ADVERTISER_API_KEY_EINTRAGEN"}}}' > "$CONFIG_DIR/config.json")
fi
printf '\nInstallation abgeschlossen.\nAPI-Key eintragen in: %s/config.json\nMCP command: %s/venv/bin/flin-chatgpt-ads-mcp\nMCP args: ["--config", "%s/config.json"]\n' "$CONFIG_DIR" "$INSTALL_DIR" "$CONFIG_DIR"
