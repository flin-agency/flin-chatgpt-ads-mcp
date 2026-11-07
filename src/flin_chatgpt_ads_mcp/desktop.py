"""Claude Desktop entry point; use only explicitly selected credentials."""

import os

from flin_chatgpt_ads_mcp.config import Config, ConfigError, load_config, validate_key


def setting(env_name, field_name):
    value = os.getenv(env_name, "").strip()
    # Some hosts leave optional, unset user_config substitutions intact.
    return "" if value == "${user_config." + field_name + "}" else value


def desktop_config():
    path = setting("FLIN_CHATGPT_ADS_CONFIG", "config_file")
    if path:
        return load_config(path)
    accounts = {}
    for number in range(1, 11):
        suffix = "" if number == 1 else f"_{number}"
        key = setting("OPENAI_ADS_API_KEY" + suffix, "api_key" + suffix)
        alias = setting("FLIN_ADS_ACCOUNT_NAME" + suffix, "account_name" + suffix)
        if not key:
            if alias:
                raise ConfigError(f"Enter an API key for account slot {number}, or clear its name in extension settings.")
            continue
        alias = alias or ("default" if number == 1 else f"konto_{number}")
        if alias in accounts:
            raise ConfigError("Account names must be unique in extension settings.")
        accounts[alias] = validate_key(key)
    if not accounts:
        raise ConfigError("Enter OpenAI Ads API keys or choose an account configuration file in the extension settings.")
    default = setting("FLIN_ADS_DEFAULT_ACCOUNT", "default_account") or None
    if default is None and len(accounts) == 1:
        default = next(iter(accounts))
    return Config(accounts, default)


if __name__ == "__main__":
    import asyncio

    from flin_chatgpt_ads_mcp.server import run

    try:
        config = desktop_config()
    except ConfigError:
        config = Config({})
    asyncio.run(run(config))
