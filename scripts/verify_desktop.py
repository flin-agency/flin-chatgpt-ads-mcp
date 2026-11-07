"""Start the built MCPB from outside the checkout against the published PyPI server.

Uses fake keys only. Calls local status/list tools; never calls the Ads API.
"""

import argparse
import asyncio
import json
import platform
import tempfile
import zipfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def verify(bundle):
    with tempfile.TemporaryDirectory(prefix="flin-desktop-verify-") as tmp:
        installed = Path(tmp) / "installation with spaces"
        with zipfile.ZipFile(bundle) as archive:
            archive.extractall(installed)
        manifest = json.loads((installed / "manifest.json").read_text())
        command = manifest["server"]["mcp_config"]
        env = {name: "" for name in command["env"]}
        env.update({"OPENAI_ADS_API_KEY": "fake-status-key-one", "FLIN_ADS_ACCOUNT_NAME": "one",
                    "OPENAI_ADS_API_KEY_10": "fake-status-key-ten", "FLIN_ADS_ACCOUNT_NAME_10": "ten"})
        (installed / ".env").write_text("FLIN_ADS_DEFAULT_ACCOUNT=one\n")
        params = StdioServerParameters(command=command["command"], args=command["args"], env=env, cwd=str(installed))
        # Reuse the installed starter, host settings and package cache on restart.
        for _ in range(2):
            async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
                initialized = await session.initialize()
                result = await session.call_tool("connection_status", {})
                assert not result.isError
                state = json.loads(result.content[0].text)
                assert state["server_version"] == initialized.serverInfo.version == manifest["version"]
                assert state["configuration_status"] == "configured"
                assert state["auth_status"] == "unknown"
                assert state["live_access"] == "not_checked"
                accounts = await session.call_tool("list_configured_accounts", {})
                assert json.loads(accounts.content[0].text) == {"accounts": ["one", "ten"], "default_account": None}
        print(f"Desktop bundle and restart verified: {manifest['version']} on {platform.system()} {platform.machine()}; no live Ads access.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    asyncio.run(verify(args.bundle.resolve()))
