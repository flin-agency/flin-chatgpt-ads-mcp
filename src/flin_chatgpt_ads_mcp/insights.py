"""Normalize common report inputs without changing account-local date boundaries."""

import json
import re
from datetime import date

METRICS = {
    "impressions",
    "clicks",
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "conversions",
    "post_click_cvr",
}
SCOPES = {
    "get_ad_account_insights": "ad_account",
    "get_campaign_insights": "campaign",
    "get_ad_group_insights": "ad_group",
    "get_ad_insights": "ad",
}


def describe_insights(operations):
    for name, scope in SCOPES.items():
        op = operations[name]
        props = op["schema"]["properties"]
        props["fields"]["description"] = (
            f"Explicit metrics to return, e.g. {scope}.impressions, {scope}.clicks, "
            f"{scope}.spend, {scope}.conversions, metadata.readable_time. "
            "Omitting fields normally returns only impressions and default metadata. "
            "Use the aggregation_level prefix for metrics; bare metric names are accepted for unsegmented reports."
        )
        props["time_ranges"]["description"] = (
            'One date range: ["2026-10-01..2026-11-02"] (both dates inclusive, account timezone), '
            'or one JSON-encoded object such as {"type":"date_range","since":"2026-10-01","until":"2026-11-02"}. '
            "unix_range uses start/end Unix seconds with exclusive end; hour_range uses since/until. "
            "Do not drop the requested date range after an error. Conversion metrics require full account-local days, at most 365 days."
        )
        props["aggregation_level"]["description"] = (
            f"Row entity; defaults to endpoint scope {scope}. Use this level as the metric prefix."
        )
        op["description"] += (
            " For clicks, spend or conversions, explicitly request fields. time_ranges accepts YYYY-MM-DD..YYYY-MM-DD inclusive in the account timezone."
        )


def normalize_insights(name, arguments):
    if name not in SCOPES:
        return arguments
    args = dict(arguments)
    if "time_ranges" in args:
        if len(args["time_ranges"]) != 1:
            raise ValueError("time_ranges requires exactly one date range.")
        value = args["time_ranges"][0]
        match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})", value)
        if match:
            since, until = match.groups()
            try:
                if date.fromisoformat(since) > date.fromisoformat(until):
                    raise ValueError
            except ValueError:
                raise ValueError(
                    "Use valid dates in ascending order: YYYY-MM-DD..YYYY-MM-DD (inclusive)."
                ) from None
            args["time_ranges"] = [
                json.dumps({"type": "date_range", "since": since, "until": until})
            ]
        else:
            try:
                decoded = json.loads(value)
            except ValueError:
                raise ValueError(
                    'time_ranges must contain YYYY-MM-DD..YYYY-MM-DD or a JSON object string, e.g. {"type":"date_range","since":"2026-10-01","until":"2026-11-02"}.'
                ) from None
            if not isinstance(decoded, dict) or decoded.get("type") not in {
                "date_range",
                "hour_range",
                "unix_range",
            }:
                raise ValueError(
                    "time_ranges requires a JSON object with type date_range, hour_range or unix_range."
                )
    if "fields" in args:
        bare = METRICS.intersection(args["fields"])
        if bare and args.get("segments"):
            raise ValueError(
                "For segmented reports, qualify metric fields explicitly, e.g. campaign.clicks or country.clicks."
            )
        level = args.get("aggregation_level", SCOPES[name])
        if level not in {"ad_account", "campaign", "ad_group", "ad"}:
            raise ValueError(
                "aggregation_level must be ad_account, campaign, ad_group or ad."
            )
        args["fields"] = [
            f"{level}.{field}" if field in METRICS else field
            for field in args["fields"]
        ]
    return args
