#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION="$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
uv build
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
BUNDLE="$STAGE/root/Applications/flin ChatGPT Ads MCP"
mkdir -p "$BUNDLE"
cp "dist/flin_chatgpt_ads_mcp-${VERSION}-py3-none-any.whl" "$BUNDLE/"
cp scripts/install.command scripts/update.command README.md examples/config.example.json "$BUNDLE/"
chmod +x "$BUNDLE/"*.command
pkgbuild --root "$STAGE/root" --identifier agency.flin.chatgpt-ads-mcp --version "$VERSION" --install-location / "dist/flin-chatgpt-ads-mcp-${VERSION}-macos.pkg"
ditto -c -k --keepParent "$BUNDLE" "dist/flin-chatgpt-ads-mcp-${VERSION}-macos.zip"
(cd dist && shasum -a 256 ./*.whl ./*.tar.gz ./*.pkg ./*.zip) > "$STAGE/SHA256SUMS"
cp "$STAGE/SHA256SUMS" dist/SHA256SUMS
