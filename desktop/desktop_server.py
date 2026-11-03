"""Fallback entry point for hosts that launch the UV entry_point directly."""

import os


def main():
    # exec preserves stdio and inherited Claude credentials without writing them.
    os.execvp(
        "uv",
        [
            "uv",
            "tool",
            "run",
            "--default-index",
            "https://pypi.org/simple",
            "flin-chatgpt-ads-mcp@latest",
            "--desktop",
        ],
    )


if __name__ == "__main__":
    main()
