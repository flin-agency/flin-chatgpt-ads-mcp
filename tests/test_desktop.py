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
        assert "uv.lock" in names
        assert "src/flin_chatgpt_ads_mcp/server.py" in names
        assert not any(".venv" in n or n.endswith("config.json") for n in names)
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["server"]["type"] == "uv"
        args = manifest["server"]["mcp_config"]["args"]
        assert args[0] == "run"
        assert "--locked" in args
        assert "--no-env-file" in args
        assert not any("latest" in arg for arg in args)
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
        assert len((await session.list_tools()).tools) == 21
        result = await session.call_tool("list_configured_accounts", {})
        assert "default" in result.content[0].text
        assert "desktop-test-key" not in result.content[0].text


async def test_extracted_bundle_stdio(tmp_path):
    """Exercise the manifest's actual launch command outside the source checkout."""
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
    params = StdioServerParameters(
        command=config["command"],
        args=[arg.replace("${__dirname}", str(extracted)) for arg in config["args"]],
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
