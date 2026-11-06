"""Build a source-only Claude Desktop bundle without credentials or local environments."""

import json
import tomllib
import zipfile
from pathlib import Path


def build(root: Path, output_dir: Path) -> Path:
    metadata = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    manifest = json.loads((root / "desktop/manifest.json").read_text())
    if manifest["version"] != metadata["version"]:
        raise ValueError("Manifest and project version must match before packaging.")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"flin-chatgpt-ads-mcp-{metadata['version']}.mcpb"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        archive.write(root / "desktop/desktop_server.py", "desktop_server.py")
        for name in ("pyproject.toml", "uv.lock"):
            archive.write(root / name, name)
        # An explicit allowlist keeps local keys, environments and stray files out.
        for name in (
            "__init__.py", "client.py", "config.py", "desktop.py", "insights.py",
            "server.py", "operations.json",
        ):
            path = Path("src/flin_chatgpt_ads_mcp") / name
            archive.write(root / path, str(path))
        archive.write(root / "README.md", "README.md")
        archive.write(root / "SECURITY.md", "SECURITY.md")
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build(root, root / "dist"))
