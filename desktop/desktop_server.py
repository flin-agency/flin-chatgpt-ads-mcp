"""Fallback for hosts that launch the entry point instead of mcp_config."""

import json
import os
import sys
from pathlib import Path


def main():
    config = json.loads(
        (Path(__file__).resolve().parent / "manifest.json").read_text()
    )["server"]["mcp_config"]
    try:
        # No shell and no credential arguments; inherit Claude's settings unchanged.
        os.execvp(config["command"], [config["command"], *config["args"]])
    except OSError:
        print("Cannot start uv. Update Claude Desktop and restart the extension.", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
