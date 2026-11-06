"""Verify that the desktop launcher's latest stable PyPI release is this release."""

import json
import subprocess
import time
import tomllib
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    expected = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    config = json.loads((root / "desktop/manifest.json").read_text())["server"]["mcp_config"]
    args = ["--version" if arg == "--desktop" else arg for arg in config["args"]]
    for attempt in range(6):
        try:
            result = subprocess.run(
                [config["command"], *args], check=False, capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0 and result.stdout.strip() == expected:
                print(f"PyPI and desktop auto-update verified: {expected}")
                return
        except subprocess.TimeoutExpired:
            pass
        if attempt < 5:
            time.sleep(10)
    raise SystemExit("The expected release is not yet available through the desktop PyPI launcher.")


if __name__ == "__main__":
    main()
