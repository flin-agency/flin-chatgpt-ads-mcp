import json
import os
import runpy
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from flin_chatgpt_ads_mcp.config import ConfigError

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_uses_explicit_key_not_default_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "desktop-test-key")
    config_path = tmp_path / ".config/flin-chatgpt-ads-mcp/config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text('{"accounts":{"unwanted":{"api_key":"other-secret"}}}')
    module = runpy.run_path(str(ROOT / "src/flin_chatgpt_ads_mcp/desktop.py"))
    assert module["desktop_config"]().select(None) == ("default", "desktop-test-key")
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", str(config_path))
    assert module["desktop_config"]().select(None) == ("unwanted", "other-secret")


def test_desktop_requires_credentials(monkeypatch):
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "")
    module = runpy.run_path(str(ROOT / "src/flin_chatgpt_ads_mcp/desktop.py"))
    with pytest.raises(ConfigError):
        module["desktop_config"]()


def test_unresolved_optional_file_uses_api_key(monkeypatch):
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "${user_config.config_file}")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "desktop-test-key")
    module = runpy.run_path(str(ROOT / "src/flin_chatgpt_ads_mcp/desktop.py"))
    assert module["desktop_config"]().select(None) == ("default", "desktop-test-key")


def test_unresolved_credentials_report_setup_error(monkeypatch):
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "${user_config.config_file}")
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "${user_config.api_key}")
    module = runpy.run_path(str(ROOT / "src/flin_chatgpt_ads_mcp/desktop.py"))
    with pytest.raises(ConfigError, match="extension settings"):
        module["desktop_config"]()


def test_selected_missing_file_does_not_switch_accounts(tmp_path, monkeypatch):
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", str(tmp_path / "missing.json"))
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "desktop-test-key")
    module = runpy.run_path(str(ROOT / "src/flin_chatgpt_ads_mcp/desktop.py"))
    with pytest.raises(ConfigError, match="Cannot open"):
        module["desktop_config"]()


def test_bundle_contents(tmp_path):
    import zipfile

    build = runpy.run_path(str(ROOT / "scripts/build_mcpb.py"))["build"]
    path = build(ROOT, tmp_path)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert "uv.lock" not in names
        assert not any(n.startswith("src/") for n in names)
        assert not any(".venv" in n or n.endswith("config.json") for n in names)
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["server"]["type"] == "uv"
        args = manifest["server"]["mcp_config"]["args"]
        assert args[:2] == ["tool", "run"]
        assert "--isolated" in args
        assert "--no-config" in args
        assert args[args.index("--prerelease") + 1] == "disallow"
        assert args[args.index("--refresh-package") + 1] == "flin-chatgpt-ads-mcp"
        assert "--no-env-file" in args
        assert args[args.index("--from") + 1] == "flin-chatgpt-ads-mcp>=0.1.6,<0.2"
        assert args[-2] == "flin-chatgpt-ads-mcp"
        assert (tmp_path / "flin-chatgpt-ads-mcp.mcpb").read_bytes() == path.read_bytes()
        assert args[-1] == "--desktop"
        assert manifest["name"] == "flin-chatgpt-ads-mcp"
        for number in range(1, 11):
            suffix = "" if number == 1 else f"_{number}"
            assert manifest["user_config"]["api_key" + suffix]["sensitive"]
            assert manifest["server"]["mcp_config"]["env"]["OPENAI_ADS_API_KEY" + suffix] == "${user_config.api_key" + suffix + "}"
        assert set(manifest["user_config"]) == {
            "config_file", "default_account", "api_key", "account_name",
            *(f"api_key_{n}" for n in range(2, 11)),
            *(f"account_name_{n}" for n in range(2, 11)),
        }


@pytest.fixture(autouse=True)
def clear_desktop_settings(monkeypatch):
    manifest = json.loads((ROOT / "desktop/manifest.json").read_text())
    for name in manifest["server"]["mcp_config"]["env"]:
        monkeypatch.delenv(name, raising=False)


def test_ten_ui_accounts_and_explicit_default(monkeypatch):
    from flin_chatgpt_ads_mcp.desktop import desktop_config

    for number in range(1, 11):
        suffix = "" if number == 1 else f"_{number}"
        monkeypatch.setenv("OPENAI_ADS_API_KEY" + suffix, f"fake-key-{number}")
        monkeypatch.setenv("FLIN_ADS_ACCOUNT_NAME" + suffix, f"client_{number}")
    config = desktop_config()
    assert len(config.accounts) == 10
    with pytest.raises(ConfigError):
        config.select(None)
    for number in range(1, 11):
        assert config.select(f"client_{number}")[1] == f"fake-key-{number}"
    monkeypatch.setenv("FLIN_ADS_DEFAULT_ACCOUNT", "client_10")
    assert desktop_config().select(None) == ("client_10", "fake-key-10")


def test_sparse_slots_and_unresolved_fields(monkeypatch):
    from flin_chatgpt_ads_mcp.desktop import desktop_config

    manifest = json.loads((ROOT / "desktop/manifest.json").read_text())
    for name, value in manifest["server"]["mcp_config"]["env"].items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("OPENAI_ADS_API_KEY_10", "test-slot-ten")
    assert desktop_config().select(None) == ("konto_10", "test-slot-ten")


@pytest.mark.parametrize("settings", [
    {"FLIN_ADS_ACCOUNT_NAME_2": "missing_key"},
    {"OPENAI_ADS_API_KEY": "test-secret", "FLIN_ADS_DEFAULT_ACCOUNT": "missing"},
    {"OPENAI_ADS_API_KEY": "test-secret", "FLIN_ADS_ACCOUNT_NAME": "test-secret"},
    {"OPENAI_ADS_API_KEY": "test-secret", "FLIN_ADS_ACCOUNT_NAME": "a/b"},
    {"OPENAI_ADS_API_KEY": "test-secret", "OPENAI_ADS_API_KEY_2": "second-secret", "FLIN_ADS_ACCOUNT_NAME_2": "default"},
])
def test_invalid_ui_settings_fail_safely(monkeypatch, settings):
    from flin_chatgpt_ads_mcp.desktop import desktop_config

    for name, value in settings.items():
        monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError) as error:
        desktop_config()
    assert "test-secret" not in str(error.value)


async def test_desktop_entrypoint_protocol():
    import sys

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "flin_chatgpt_ads_mcp.server", "--desktop"],
        env={
            **os.environ,
            "OPENAI_ADS_API_KEY": "desktop-test-key",
            "FLIN_CHATGPT_ADS_CONFIG": "${user_config.config_file}",
        },
    )
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        assert len((await session.list_tools()).tools) == 22
        result = await session.call_tool("list_configured_accounts", {})
        assert "default" in result.content[0].text
        assert "desktop-test-key" not in result.content[0].text


async def test_extracted_bundle_stdio(tmp_path):
    """Launch the candidate wheel through uv before it is published to PyPI."""
    import asyncio
    import subprocess
    import zipfile

    build = runpy.run_path(str(ROOT / "scripts/build_mcpb.py"))["build"]
    bundle = build(ROOT, tmp_path)
    extracted = tmp_path / "installation with spaces"
    with zipfile.ZipFile(bundle) as archive:
        archive.extractall(extracted)
    manifest = json.loads((extracted / "manifest.json").read_text())
    config = manifest["server"]["mcp_config"]
    # Unset optional fields may be empty strings or unresolved substitutions.
    env = dict(config["env"])
    env.update({"OPENAI_ADS_API_KEY": "fake-bundle-alpha", "FLIN_ADS_ACCOUNT_NAME": "alpha",
                "OPENAI_ADS_API_KEY_10": "fake-bundle-beta", "FLIN_ADS_ACCOUNT_NAME_10": "beta"})
    # The launcher must not import credentials from an adjacent .env file.
    (extracted / ".env").write_text("FLIN_ADS_DEFAULT_ACCOUNT=alpha\n")
    wheel_dir = tmp_path / "wheels"
    await asyncio.to_thread(
        subprocess.run, ["uv", "build", "--wheel", "--out-dir", str(wheel_dir), str(ROOT)], check=True
    )
    wheel = next(wheel_dir.glob("*.whl"))
    args = list(config["args"])
    args[args.index("--from") + 1] = str(wheel)
    params = StdioServerParameters(
        command=config["command"],
        args=args,
        cwd=str(extracted),
        env=env,
    )
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        initialized = await session.initialize()
        assert initialized.serverInfo.version == manifest["version"]
        result = await session.call_tool("list_configured_accounts", {})
        assert json.loads(result.content[0].text) == {"accounts": ["alpha", "beta"], "default_account": None}
        ambiguous = await session.call_tool("get_ad_account", {})
        assert ambiguous.isError
        assert "fake-bundle" not in str(result)
        status = await session.call_tool("connection_status", {})
        state = json.loads(status.content[0].text)
        assert state["server_version"] == manifest["version"]
        assert state["configuration_status"] == "configured"
        assert state["auth_status"] == "unknown"
        assert state["live_access"] == "not_checked"


def test_fallback_uses_same_command_and_preserves_credentials(monkeypatch):
    monkeypatch.setenv("OPENAI_ADS_API_KEY_10", "unchanged-test-key")
    monkeypatch.setenv("FLIN_ADS_ACCOUNT_NAME_10", "client_ten")
    monkeypatch.setenv("FLIN_CHATGPT_ADS_CONFIG", "/path/to/accounts.json")
    before = dict(os.environ)
    calls = []
    monkeypatch.setattr(os, "execvp", lambda command, args: calls.append((command, args)))
    module = runpy.run_path(str(ROOT / "desktop/desktop_server.py"))
    module["main"]()
    config = json.loads((ROOT / "desktop/manifest.json").read_text())["server"]["mcp_config"]
    assert calls == [(config["command"], [config["command"], *config["args"]])]
    assert dict(os.environ) == before
    assert "unchanged-test-key" not in str(calls)


def test_launcher_refreshes_cached_version_and_excludes_prereleases(tmp_path):
    """A local wheel source simulates new releases without publishing test packages."""
    import subprocess
    import zipfile

    wheel_dir = tmp_path / "index"
    wheel_dir.mkdir()

    def publish(version):
        dist = f"flin_chatgpt_ads_mcp-{version}.dist-info"
        with zipfile.ZipFile(wheel_dir / f"flin_chatgpt_ads_mcp-{version}-py3-none-any.whl", "w") as wheel:
            wheel.writestr("test_launcher_probe.py", 'import json, os\ndef main():\n    print(json.dumps({"version": "' + version + '", "settings": {k: os.getenv(k) for k in ("OPENAI_ADS_API_KEY", "OPENAI_ADS_API_KEY_10", "FLIN_ADS_ACCOUNT_NAME_10", "FLIN_CHATGPT_ADS_CONFIG")}}))\n')
            wheel.writestr(dist + "/METADATA", f"Metadata-Version: 2.1\nName: flin-chatgpt-ads-mcp\nVersion: {version}\n")
            wheel.writestr(dist + "/WHEEL", "Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
            wheel.writestr(dist + "/entry_points.txt", "[console_scripts]\nflin-chatgpt-ads-mcp = test_launcher_probe:main\n")
            wheel.writestr(dist + "/RECORD", "")

    config = json.loads((ROOT / "desktop/manifest.json").read_text())["server"]["mcp_config"]
    args = list(config["args"])
    args[2:2] = ["--no-index", "--find-links", str(wheel_dir), "--cache-dir", str(tmp_path / "cache")]

    saved_file = tmp_path / "existing-accounts.json"
    saved_file.write_text('{"accounts":{"existing":{"api_key":"fake-saved-key"}}}')
    saved_content = saved_file.read_bytes()
    settings = {"OPENAI_ADS_API_KEY": "fake-ui-key", "OPENAI_ADS_API_KEY_10": "fake-tenth-key",
                "FLIN_ADS_ACCOUNT_NAME_10": "tenth", "FLIN_CHATGPT_ADS_CONFIG": str(saved_file)}

    def launch():
        result = subprocess.run([config["command"], *args], env={**os.environ, **settings},
                                capture_output=True, text=True, timeout=30, check=True)
        data = json.loads(result.stdout)
        assert data["settings"] == settings
        assert saved_file.read_bytes() == saved_content
        return data["version"]

    publish("0.1.6")
    assert launch() == "0.1.6"
    publish("0.1.7")
    publish("0.1.8rc1")
    publish("0.2.0")
    publish("1.0.0")
    assert launch() == "0.1.7"
    assert launch() == "0.1.7"
