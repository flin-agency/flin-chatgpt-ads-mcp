import json

import pytest

from flin_chatgpt_ads_mcp.config import ConfigError, load_config


def test_file_and_env_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_ADS_KEY", "second-secret")
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "accounts": {
                    "first": {"api_key": "first-secret"},
                    "second": {"api_key_env": "TEST_ADS_KEY"},
                },
                "default_account": "first",
            }
        )
    )
    config = load_config(str(path))
    assert config.select(None) == ("first", "first-secret")
    assert config.select("second") == ("second", "second-secret")
    assert "secret" not in repr(config)


@pytest.mark.parametrize(
    "data",
    [
        [],
        {"accounts": []},
        {"accounts": {"a": {"api_key": ""}}},
        {"accounts": {"a": {"api_key": "secret", "api_key_env": "FOO"}}},
        {"default_account": "missing"},
        {"accounts": {"a": {"api_key_env": "FLIN_TEST_MISSING_ENV"}}},
    ],
)
def test_invalid_config(tmp_path, data):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError):
        load_config(str(path))


def test_single_env_key(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("FLIN_CHATGPT_ADS_CONFIG", raising=False)
    monkeypatch.setenv("OPENAI_ADS_API_KEY", "env-secret")
    assert load_config().select(None) == ("default", "env-secret")
