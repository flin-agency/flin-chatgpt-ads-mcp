"""Account credentials are configuration only, never tool arguments."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(ValueError):
    pass


@dataclass(repr=False)
class Config:
    accounts: dict[str, str] = field(repr=False)
    default_account: str | None = None

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
            data = json.loads(location.read_text())
        except (OSError, ValueError):
            raise ConfigError("Cannot read configuration JSON.") from None
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
        if env_name is not None and not isinstance(env_name, str):
            raise ConfigError("api_key_env must name an environment variable.")
        key = os.getenv(env_name, "") if env_name else entry.get("api_key")
        if not isinstance(key, str) or not key.strip() or any(c.isspace() for c in key):
            raise ConfigError("An account API key is missing or invalid.")
        accounts[alias] = key
    if not accounts and os.getenv("OPENAI_ADS_API_KEY"):
        key = os.environ["OPENAI_ADS_API_KEY"]
        if any(c.isspace() for c in key):
            raise ConfigError("OPENAI_ADS_API_KEY contains whitespace.")
        accounts["default"] = key
    default = data.get("default_account")
    if default is not None and (
        not isinstance(default, str) or default not in accounts
    ):
        raise ConfigError("default_account must reference a configured account.")
    return Config(accounts, default)
