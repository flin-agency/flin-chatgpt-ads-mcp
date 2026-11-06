"""Account credentials are configuration only, never tool arguments."""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(ValueError):
    pass


def validate_key(key):
    # HTTP header values must be printable ASCII, never control characters.
    if not isinstance(key, str) or not key or not all(33 <= ord(c) <= 126 for c in key):
        raise ConfigError("An account API key is missing or invalid.")
    return key


@dataclass(repr=False)
class Config:
    accounts: dict[str, str] = field(repr=False)
    default_account: str | None = None

    def __post_init__(self):
        for key in self.accounts.values():
            validate_key(key)
        for alias in self.accounts:
            if not isinstance(alias, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", alias):
                raise ConfigError("Account names must use 1–64 letters, numbers, underscores or hyphens.")
            if any(secret in alias for secret in self.accounts.values()):
                raise ConfigError("Account names must not contain API keys.")
        if self.default_account is not None and (
            not isinstance(self.default_account, str)
            or self.default_account not in self.accounts
        ):
            raise ConfigError("default_account must reference a configured account.")

    def select(self, alias: str | None) -> tuple[str, str]:
        selected = alias or self.default_account
        if not selected and len(self.accounts) == 1:
            selected = next(iter(self.accounts))
        if selected not in self.accounts:
            raise ConfigError("Choose an account alias from list_configured_accounts.")
        return selected, self.accounts[selected]


def load_config(path: str | None = None) -> Config:
    explicit = path or os.getenv("FLIN_CHATGPT_ADS_CONFIG")
    location = (
        Path(explicit).expanduser()
        if explicit
        else Path.home() / ".config/flin-chatgpt-ads-mcp/config.json"
    )
    data = {}
    if explicit or location.exists():
        try:
            data = json.loads(location.read_text(encoding="utf-8"))
        except OSError:
            raise ConfigError(
                "Cannot open the selected account configuration file. Check that it exists and is readable, or clear the optional file setting to use API keys from extension settings."
            ) from None
        except (ValueError, UnicodeError, RecursionError):
            raise ConfigError(
                "The selected account configuration file must contain valid UTF-8 JSON. Choose a valid JSON file, or clear the optional file setting to use API keys from extension settings."
            ) from None
    if not isinstance(data, dict) or set(data) - {"accounts", "default_account"}:
        raise ConfigError("Configuration accepts accounts and default_account only.")
    entries = data.get("accounts", {})
    if not isinstance(entries, dict):
        raise ConfigError("accounts must be an object keyed by account alias.")
    accounts = {}
    for alias, entry in entries.items():
        if (
            not isinstance(alias, str)
            or not alias.strip()
            or not isinstance(entry, dict)
        ):
            raise ConfigError("Invalid account entry.")
        if set(entry) - {"api_key", "api_key_env"} or len(entry) != 1:
            raise ConfigError(
                "Each account requires exactly one of api_key or api_key_env."
            )
        env_name = entry.get("api_key_env")
        if "api_key_env" in entry and (
            not isinstance(env_name, str)
            or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", env_name)
        ):
            raise ConfigError("api_key_env must name an environment variable.")
        key = os.getenv(env_name, "") if env_name else entry.get("api_key")
        accounts[alias] = validate_key(key)
    if not explicit and not location.exists() and os.getenv("OPENAI_ADS_API_KEY"):
        key = os.environ["OPENAI_ADS_API_KEY"]
        accounts["default"] = validate_key(key)
    default = data.get("default_account")
    if default is not None and (
        not isinstance(default, str) or default not in accounts
    ):
        raise ConfigError("default_account must reference a configured account.")
    return Config(accounts, default)
