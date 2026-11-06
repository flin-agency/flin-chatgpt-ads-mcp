import json

import httpx
import pytest
from jsonschema import Draft202012Validator

from flin_chatgpt_ads_mcp.client import OPERATIONS, AdsClient, AdsError
from flin_chatgpt_ads_mcp.config import Config, ConfigError


@pytest.fixture
def config():
    return Config({"alpha": "secret-alpha-key", "beta": "secret-beta-key"})


async def test_account_selection_and_pagination(config):
    def handler(request):
        assert request.method == "GET"
        assert request.url.host == "api.ads.openai.com"
        assert request.url.path == "/v1/campaigns"
        assert request.headers["Authorization"] == "Bearer secret-beta-key"
        assert dict(request.url.params) == {"after": "cmpn_previous", "limit": "10"}
        return httpx.Response(
            200, json={"data": [], "has_more": True, "last_id": "next"}
        )

    result = await AdsClient(config, httpx.MockTransport(handler)).call(
        "list_campaigns", {"account": "beta", "after": "cmpn_previous", "limit": 10}
    )
    assert result["account"] == "beta"
    assert result["result"]["has_more"] is True


async def test_reporting_serialization(config):
    time_range = json.dumps(
        {"type": "unix_range", "start": 1777075200, "end": 1777248000}
    )

    def handler(request):
        assert request.url.params.get_list("fields[]") == [
            "campaign.id",
            "campaign.spend",
        ]
        assert request.url.params["time_ranges[]"] == time_range
        assert request.url.params["view_through_attribution_window_days"] == "0"
        return httpx.Response(200, json={"data": [{"spend": None}]})

    result = await AdsClient(config, httpx.MockTransport(handler)).call(
        "get_ad_account_insights",
        {
            "account": "alpha",
            "fields": ["campaign.id", "campaign.spend"],
            "time_ranges": [time_range],
            "view_through_attribution_window_days": 0,
        },
    )
    assert result["result"]["data"][0]["spend"] is None


@pytest.mark.parametrize(
    "name,args",
    [
        ("delete_campaign", {}),
        ("get_campaign", {"campaign_id": "../ads"}),
        ("get_campaign", {"campaign_id": "%2e%2e"}),
        ("get_campaign", {}),
        ("list_campaigns", {"limit": 501}),
        ("list_campaigns", {"url": "https://example.org"}),
        ("list_campaigns", {"after": "a", "before": "b"}),
        ("get_ad_account_insights", {"attribution_window_days": 8}),
    ],
)
async def test_rejected_without_network(config, name, args):
    def handler(request):
        pytest.fail("Invalid input reached network")

    with pytest.raises(AdsError):
        await AdsClient(config, httpx.MockTransport(handler)).call(
            name, {"account": "alpha", **args}
        )


async def test_ambiguous_account(config):
    with pytest.raises(ConfigError):
        await AdsClient(config).call("get_ad_account", {})


@pytest.mark.parametrize("status", [301, 401, 403, 500])
async def test_errors_and_redirects_do_not_leak_secrets(config, status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status, text="secret-alpha-key", headers={"Location": "https://example.org"}
        )

    with pytest.raises(AdsError) as error:
        await AdsClient(config, httpx.MockTransport(handler)).call(
            "get_ad_account", {"account": "alpha"}
        )
    assert "secret-alpha-key" not in str(error.value)
    assert len(calls) == 1


async def test_retry(config, monkeypatch):
    calls = []

    async def sleep(delay):
        pass

    monkeypatch.setattr("flin_chatgpt_ads_mcp.client.asyncio.sleep", sleep)

    def handler(request):
        calls.append(request)
        return httpx.Response(429 if len(calls) < 3 else 200, json={"ok": True})

    await AdsClient(config, httpx.MockTransport(handler)).call(
        "get_ad_account", {"account": "alpha"}
    )
    assert len(calls) == 3


async def test_success_redacts_keys(config):
    transport = httpx.MockTransport(
        lambda r: httpx.Response(200, json={"echo": "secret-beta-key"})
    )
    result = await AdsClient(config, transport).call(
        "get_ad_account", {"account": "alpha"}
    )
    assert result["result"]["echo"] == "[REDACTED]"


@pytest.mark.parametrize("name", OPERATIONS)
async def test_every_registered_operation_uses_get(config, name):
    op = OPERATIONS[name]
    Draft202012Validator.check_schema(op["schema"])
    args = {"account": "alpha"}
    for key in op["schema"].get("required", []):
        args[key] = "test_123"

    def handler(request):
        assert request.method == "GET"
        assert request.url.host == "api.ads.openai.com"
        return httpx.Response(200, json={"ok": True})

    await AdsClient(config, httpx.MockTransport(handler)).call(name, args)


async def test_nested_and_escaped_secrets_are_redacted():
    key = 'secret-"-\\-key'
    config = Config({"alpha": key, "beta": "other-key"})
    transport = httpx.MockTransport(lambda r: httpx.Response(
        200, json={key: [{"echo": key + " other-key"}], "number": 123, "empty": None}
    ))
    result = await AdsClient(config, transport).call("get_ad_account", {"account": "alpha"})
    assert result["result"] == {"[REDACTED]": [{"echo": "[REDACTED] [REDACTED]"}], "number": 123, "empty": None}


async def test_large_response_is_rejected(config, monkeypatch):
    monkeypatch.setattr("flin_chatgpt_ads_mcp.client.MAX_RESPONSE_BYTES", 32)
    transport = httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * 33))
    with pytest.raises(AdsError, match="too large"):
        await AdsClient(config, transport).call("get_ad_account", {"account": "alpha"})


@pytest.mark.parametrize("body", [b"secret-alpha-key", b'"\xff"', b"[" * 2000 + b"]" * 2000])
async def test_invalid_json_is_safe(config, body):
    transport = httpx.MockTransport(lambda r: httpx.Response(200, content=body))
    with pytest.raises(AdsError, match="invalid JSON") as error:
        await AdsClient(config, transport).call("get_ad_account", {"account": "alpha"})
    assert "secret-alpha-key" not in str(error.value)


@pytest.mark.parametrize("delay", ["999999999999999", "²", "11", "tomorrow", "-1"])
async def test_invalid_retry_delay_is_bounded(config, delay):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(429, headers={"Retry-After": delay.encode("utf-8")})

    with pytest.raises(AdsError, match="429"):
        await AdsClient(config, httpx.MockTransport(handler)).call("get_ad_account", {"account": "alpha"})
    assert len(calls) == 1


async def test_network_errors_hide_credentials(config):
    def handler(request):
        raise httpx.ConnectError("secret-alpha-key", request=request)

    with pytest.raises(AdsError) as error:
        await AdsClient(config, httpx.MockTransport(handler)).call("get_ad_account", {"account": "alpha"})
    assert "secret-alpha-key" not in str(error.value)


async def test_overall_deadline(config, monkeypatch):
    import asyncio

    monkeypatch.setattr("flin_chatgpt_ads_mcp.client.MAX_REQUEST_SECONDS", 0.01)

    async def handler(request):
        await asyncio.sleep(1)
        pytest.fail("Deadline did not cancel request")

    with pytest.raises(AdsError, match="timed out"):
        await AdsClient(config, httpx.MockTransport(handler)).call("get_ad_account", {"account": "alpha"})


async def test_environment_proxy_is_ignored(config, monkeypatch):
    original = httpx.AsyncClient
    seen = []

    def client(**kwargs):
        seen.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client)
    monkeypatch.setenv("HTTPS_PROXY", "http://untrusted.invalid:8080")
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    await AdsClient(config, transport).call("get_ad_account", {"account": "alpha"})
    assert seen[0]["trust_env"] is False
    assert seen[0]["follow_redirects"] is False
