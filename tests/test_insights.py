import json

import httpx
import pytest

from flin_chatgpt_ads_mcp.client import OPERATIONS, AdsClient, AdsError
from flin_chatgpt_ads_mcp.config import Config


async def test_reported_requests_are_normalized_without_losing_dates():
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json={"data": []})

    client = AdsClient(Config({"test": "test-key"}), httpx.MockTransport(handle))
    await client.call(
        "get_campaign_insights",
        {
            "campaign_id": "cmpn_test",
            "time_granularity": "daily",
            "time_ranges": ["2026-10-01..2026-11-02"],
            "fields": ["impressions", "clicks", "spend", "conversions"],
            "limit": 100,
        },
    )
    query = seen[0].url.params
    assert json.loads(query["time_ranges[]"]) == {
        "type": "date_range",
        "since": "2026-10-01",
        "until": "2026-11-02",
    }
    assert query.get_list("fields[]") == [
        "campaign.impressions",
        "campaign.clicks",
        "campaign.spend",
        "campaign.conversions",
    ]
    assert seen[0].method == "GET"


@pytest.mark.parametrize(
    "name,level",
    [
        ("get_ad_account_insights", "ad_account"),
        ("get_campaign_insights", "campaign"),
        ("get_ad_group_insights", "ad_group"),
        ("get_ad_insights", "ad"),
    ],
)
async def test_scope_and_explicit_aggregation(name, level):
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(200, json={})

    client = AdsClient(Config({"test": "test-key"}), httpx.MockTransport(handle))
    args = {k: "id_test" for k in OPERATIONS[name]["schema"].get("required", [])}
    await client.call(name, {**args, "fields": ["clicks", "metadata.readable_time"]})
    assert seen[-1].url.params.get_list("fields[]") == [
        f"{level}.clicks",
        "metadata.readable_time",
    ]
    await client.call(name, {**args, "aggregation_level": "ad", "fields": ["clicks"]})
    assert seen[-1].url.params["fields[]"] == "ad.clicks"


@pytest.mark.parametrize(
    "args",
    [
        {"time_ranges": ["2026-02-30..2026-03-01"]},
        {"time_ranges": ["2026-11-02..2026-10-01"]},
        {"time_ranges": ["October"]},
        {"time_ranges": []},
        {"time_ranges": ['"plain string"']},
        {"fields": ["clicks"], "segments": ["country"]},
    ],
)
async def test_invalid_or_ambiguous_inputs_never_reach_api(args):
    def handle(request):
        pytest.fail("Invalid report reached API")

    client = AdsClient(Config({"test": "test-key"}), httpx.MockTransport(handle))
    with pytest.raises(AdsError):
        await client.call("get_campaign_insights", {"campaign_id": "cmpn_test", **args})


async def test_explicit_json_and_segment_fields_preserved():
    value = '{"type":"date_range","since":"2026-10-01","until":"2026-11-02","timezone":"Europe/Zurich"}'

    def handle(request):
        assert request.url.params["time_ranges[]"] == value
        assert request.url.params.get_list("fields[]") == [
            "country.clicks",
            "campaign.id",
        ]
        return httpx.Response(200, json={})

    client = AdsClient(Config({"test": "test-key"}), httpx.MockTransport(handle))
    await client.call(
        "get_campaign_insights",
        {
            "campaign_id": "cmpn_test",
            "time_ranges": [value],
            "segments": ["country"],
            "fields": ["country.clicks", "campaign.id"],
        },
    )
