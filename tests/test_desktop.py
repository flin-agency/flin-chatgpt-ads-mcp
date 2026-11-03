import json
import os
import runpy
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from flin_chatgpt_ads_mcp.config import ConfigError

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_uses_explicit_key_not_default_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "desktop-test-key")
    config_path = tmp_path / ".config/flin-chatgpt-ads-mcp/config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text('{"accounts":{"unwanted":{"api_key":"other-secret"}}}')
    module = runpy.run_path(str(ROOT / "desktop/desktop_server.py"))
    assert module["desktop_config"]().select(None) == ("default", "desktop-test-key")
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", str(config_path))
    assert module["desktop_config"]().select(None) == ("unwanted", "other-secret")


def test_desktop_requires_credentials(monkeypatch):
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "")
    module = runpy.run_path(str(ROOT / "desktop/desktop_server.py"))
    with pytest.raises(ConfigError):
        module["desktop_config"]()


def test_bundle_contents(tmp_path):
    import zipfile

    build = runpy.run_path(str(ROOT / "scripts/build_mcpb.py"))["build"]
    path = build(ROOT, tmp_path)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert "uv.lock" in names
        assert "src/flin_chatgpt_ads_mcp/operations.json" in names
        assert not any(".venv" in n or n.endswith("config.json") for n in names)
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["server"]["type"] == "uv"
        assert manifest["user_config"]["api_key"]["sensitive"]


async def test_desktop_entrypoint_protocol():
    import sys

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "desktop/desktop_server.py")],
        env={
            **os.environ,
            "OPENAI_ADS_API_KEY": "desktop-test-key",
            "FLIN_CHATGPT_ADS_CONFIG": "",
        },
    )
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        assert len((await session.list_tools()).tools) == 21
        result = await session.call_tool("list_configured_accounts", {})
        assert "default" in result.content[0].text
        assert "desktop-test-key" not in result.content[0].text
