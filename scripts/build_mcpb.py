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
        for name in ("pyproject.toml", "uv.lock", "README.md"):
            archive.write(root / name, name)
        for path in sorted((root / "src/flin_chatgpt_ads_mcp").iterdir()):
            if path.suffix in {".py", ".json"} and path.is_file():
                archive.write(path, path.relative_to(root))
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build(root, root / "dist"))
