import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_real_stdio_handshake_and_tool_call(tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"accounts":{"test":{"api_key":"fake-advertiser-key"}}}')
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "flin_chatgpt_ads_mcp.server", "--config", str(config)],
        env=dict(os.environ),
    )
    async with (
        stdio_client(parameters) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        tools = (await session.list_tools()).tools
        assert len(tools) == 21
        assert all(
            t.annotations.readOnlyHint and not t.annotations.destructiveHint
            for t in tools
        )
        result = await session.call_tool("list_configured_accounts", {})
        assert not result.isError
        assert "test" in result.content[0].text
        assert "fake-advertiser-key" not in result.content[0].text
        invalid = await session.call_tool("get_campaign", {"campaign_id": "../ads"})
        assert invalid.isError
