"""Fixed origin, allowlisted GET requests, no redirects or raw HTTP tool."""

import asyncio
import json
import re
from importlib.resources import files

import httpx
from jsonschema import Draft202012Validator

from .config import Config
from .insights import describe_insights, normalize_insights

OPERATIONS = json.loads(files(__package__).joinpath("operations.json").read_text())
describe_insights(OPERATIONS)
BASE_URL = "https://api.ads.openai.com/v1"


class AdsError(ValueError):
    pass


class AdsClient:
    def __init__(self, config: Config, transport=None):
        self.config = config
        self.transport = transport

    async def call(self, name: str, arguments: dict):
        if name not in OPERATIONS:
            raise AdsError("Unknown or unsupported read-only operation.")
        op = OPERATIONS[name]
        errors = list(Draft202012Validator(op["schema"]).iter_errors(arguments))
        if errors:
            # Validation messages may contain input values, including secrets.
            raise AdsError("Invalid tool arguments. Check the tool input schema.")
        try:
            arguments = normalize_insights(name, arguments)
        except ValueError as exc:
            raise AdsError(str(exc)) from None
        alias, key = self.config.select(arguments.get("account"))
        path = op["path"]
        params = []
        for param in op["parameters"]:
            name = param["name"]
            if name not in arguments:
                continue
            value = arguments[name]
            if param["in"] == "path":
                if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
                    raise AdsError(
                        "Resource IDs may contain letters, numbers, underscores and hyphens only."
                    )
                path = path.replace("{" + name + "}", value)
            elif isinstance(value, list):
                params.extend((name + "[]", str(v)) for v in value)
            else:
                params.append(
                    (
                        name,
                        str(value).lower() if isinstance(value, bool) else str(value),
                    )
                )
        if arguments.get("after") and arguments.get("before"):
            raise AdsError("Use either after or before, not both.")
        async with httpx.AsyncClient(
            transport=self.transport,
            timeout=30,
            follow_redirects=False,
            trust_env=False,
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        ) as client:
            for attempt in range(3):
                try:
                    response = await client.get(BASE_URL + path, params=params)
                except httpx.HTTPError:
                    raise AdsError(
                        "Ads API network request failed; please retry."
                    ) from None
                if response.status_code in (429, 502, 503, 504) and attempt < 2:
                    delay = response.headers.get("Retry-After", "")
                    if delay.isdigit() and int(delay) > 10:
                        break
                    await asyncio.sleep(int(delay) if delay.isdigit() else 2**attempt)
                    continue
                break
        if not 200 <= response.status_code < 300:
            hints = {
                401: "Check the account API key.",
                403: "Check account access.",
                429: "Rate limit reached; retry later.",
            }
            raise AdsError(
                f"Ads API HTTP {response.status_code}. {hints.get(response.status_code, 'Request failed. Check parameters and account availability.')}"
            )
        try:
            result = response.json()
        except ValueError:
            raise AdsError("Ads API returned an invalid JSON response.") from None
        # Never expose a configured key, even if an upstream response echoes it.
        encoded = json.dumps(result, ensure_ascii=False)
        for secret in self.config.accounts.values():
            encoded = encoded.replace(json.dumps(secret)[1:-1], "[REDACTED]")
        return {"account": alias, "result": json.loads(encoded)}
