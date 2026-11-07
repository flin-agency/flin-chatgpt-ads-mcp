"""Build a Claude Desktop auto-update launcher without credentials."""

import json
import shutil
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
        # The host needs no server dependencies to run this fallback launcher.
        archive.writestr(
            "pyproject.toml",
            '[project]\nname = "flin-chatgpt-ads-launcher"\n'
            f'version = "{metadata["version"]}"\nrequires-python = ">=3.11"\n'
            "dependencies = []\n\n[tool.uv]\npackage = false\n",
        )
        archive.write(root / "README.md", "README.md")
        for name in ("SECURITY.md", "PRIVACY.md", "SUPPORT.md"):
            archive.write(root / name, name)
        archive.write(root / "docs/security-review-0.1.5.md", "docs/security-review-0.1.5.md")
    shutil.copyfile(output, output_dir / "flin-chatgpt-ads-mcp.mcpb")
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build(root, root / "dist"))
