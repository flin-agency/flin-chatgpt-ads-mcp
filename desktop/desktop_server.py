"""Claude Desktop entry point; use only explicitly selected credentials."""

import asyncio
import os
import sys

from flin_chatgpt_ads_mcp.config import Config, ConfigError, load_config
from flin_chatgpt_ads_mcp.server import run


def desktop_config():
    path = os.getenv("FLIN_CHATGPT_ADS_CONFIG", "").strip()
    if path:
        return load_config(path)
    key = os.getenv("OPENAI_ADS_API_KEY", "").strip()
    if key:
        if not key.isascii() or any(c.isspace() for c in key):
            raise ConfigError("Invalid Advertiser API key in extension settings.")
        return Config({"default": key}, "default")
    raise ConfigError(
        "Enter an OpenAI Ads API key or choose an account configuration file in the extension settings."
    )


if __name__ == "__main__":
    try:
        asyncio.run(run(desktop_config()))
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from None
