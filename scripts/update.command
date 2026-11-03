#!/bin/bash
set -euo pipefail
INSTALL_DIR="${FLIN_ADS_INSTALL_DIR:-$HOME/.local/share/flin-chatgpt-ads-mcp}"
PYTHON="$INSTALL_DIR/venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  echo 'Bitte zuerst install.command ausführen.' >&2
  exit 1
fi
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$PYTHON" --upgrade flin-chatgpt-ads-mcp
elif [ -x "$HOME/.local/bin/uv" ]; then
  "$HOME/.local/bin/uv" pip install --python "$PYTHON" --upgrade flin-chatgpt-ads-mcp
else
  "$PYTHON" -m ensurepip
  "$PYTHON" -m pip install --upgrade flin-chatgpt-ads-mcp
fi
echo 'Update abgeschlossen. Bitte den MCP-Client neu starten.'
