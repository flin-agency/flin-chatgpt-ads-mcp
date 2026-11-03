"""Build a source-only Claude Desktop bundle without credentials or local environments."""

import json
import tomllib
import zipfile
from pathlib import Path


def build(root: Path, output_dir: Path) -> Path:
    metadata = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    manifest = json.loads((root / "desktop/manifest.json").read_text())
    manifest["version"] = metadata["version"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"flin-chatgpt-ads-mcp-{metadata['version']}.mcpb"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        archive.write(root / "desktop/desktop_server.py", "desktop_server.py")
        archive.writestr(
            "pyproject.toml",
            '[project]\nname = "flin-chatgpt-ads-launcher"\n'
            f'version = "{metadata["version"]}"\nrequires-python = ">=3.11"\n'
            "dependencies = []\n\n[tool.uv]\npackage = false\n",
        )
        archive.write(root / "README.md", "README.md")
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build(root, root / "dist"))
