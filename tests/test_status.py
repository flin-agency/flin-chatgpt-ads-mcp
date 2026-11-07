import json
import os
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.memory import create_connected_server_and_client_session

from flin_chatgpt_ads_mcp import __version__
from flin_chatgpt_ads_mcp.config import Config
from flin_chatgpt_ads_mcp.server import create_server


@pytest.mark.parametrize("accounts", [{}, {"private_alias": "fake-private-key"}])
async def test_status_is_local_and_has_no_secrets(accounts, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Local status attempted network or browser access")

    monkeypatch.setattr("httpx.AsyncClient", forbidden)
    monkeypatch.setattr("webbrowser.open", forbidden)
    async with create_connected_server_and_client_session(create_server(Config(accounts))) as session:
        result = await session.call_tool("connection_status", {})
        assert not result.isError
        data = json.loads(result.content[0].text)
        assert set(data) == {"server_version", "configuration_status", "auth_status", "live_access", "next_step"}
        assert data["server_version"] == __version__
        assert data["configuration_status"] == ("configured" if accounts else "incomplete")
        assert data["auth_status"] == ("unknown" if accounts else "unauthenticated")
        assert data["live_access"] == "not_checked"
        assert data["next_step"]
        assert "private" not in result.content[0].text
        tools = (await session.list_tools()).tools
        assert next(t for t in tools if t.name == "connection_status").annotations.openWorldHint is False
        invalid = await session.call_tool("connection_status", {"live": True, "key": "fake-private-key"})
        assert invalid.isError
        assert "fake-private-key" not in invalid.content[0].text


@pytest.mark.parametrize("mode", ["empty", "invalid_ui", "missing_file", "invalid_file"])
async def test_incomplete_setup_keeps_status_available_and_api_closed(tmp_path, mode):
    # Start without inheriting local credentials.
    env = {"PATH": os.environ["PATH"], "FLIN_CHATGPT_ADS_CONFIG": "", "OPENAI_ADS_API_KEY": ""}
    if mode == "invalid_ui":
        env["FLIN_ADS_ACCOUNT_NAME"] = "name_without_key"
    elif mode in {"missing_file", "invalid_file"}:
        path = tmp_path / "accounts.json"
        if mode == "invalid_file":
            path.write_text("this is not JSON")
        env.update({"FLIN_CHATGPT_ADS_CONFIG": str(path), "OPENAI_ADS_API_KEY": "must-not-fallback"})
    params = StdioServerParameters(command=sys.executable, args=["-m", "flin_chatgpt_ads_mcp.server", "--desktop"], env=env)
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("connection_status", {})
        state = json.loads(result.content[0].text)
        assert state["configuration_status"] == "incomplete"
        assert state["auth_status"] == "unauthenticated"
        assert state["live_access"] == "not_checked"
        accounts = await session.call_tool("list_configured_accounts", {})
        assert json.loads(accounts.content[0].text) == {"accounts": [], "default_account": None}
        blocked = await session.call_tool("get_ad_account", {})
        assert blocked.isError
        assert "must-not-fallback" not in str(result)
