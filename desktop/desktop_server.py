"""Run the reviewed server source included in this bundle."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from flin_chatgpt_ads_mcp.config import ConfigError
from flin_chatgpt_ads_mcp.desktop import desktop_config
from flin_chatgpt_ads_mcp.server import run


def main():
    try:
        asyncio.run(run(desktop_config()))
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
