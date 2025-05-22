import json
from collections.abc import Generator
from datetime import datetime
from time import sleep, time
from typing import Literal, cast

import click
import requests

from better_timetagger_cli.lib.utils import abort

from .config import load_config
from .types import GetRecordsResponse, GetSettingsResponse, GetUpdatesResponse, PutRecordsResponse, PutSettingsResponse, Record, Settings


def _request(
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    path: str,
    body: list | dict | None = None,
) -> dict:
    """
    Execute an authenticated request to the Timetagger API.

    Args:
        method: The HTTP method to use.
        path: The API endpoint path.
        body: The request body to send. Defaults to None.

    Returns:
        The JSON-decoded response from the API.
    """
    try:
        config = load_config()
        url = config["api_url"].rstrip("/") + "/" + path.lstrip("/")
        token = config["api_token"].strip()
        ssl_verify = config["ssl_verify"]

        headers = {"authtoken": token}
        response = requests.request(method.upper(), url, json=body, headers=headers, verify=ssl_verify)

    except Exception as e:
        abort(f"API request failed: {e.__class__.__name__}\n[dim]{e}[/dim]")

    if response.status_code != 200:
        response_text = response.text
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            pass
        abort(f"API request failed with status code: {response.status_code}\n[dim]{response_text}[/dim]")
        raise click.Abort

    return response.json()


def _normalize_records(records: list[Record]) -> list[Record]:
    """
    Ensure that all records have the required keys with expected types.

    Args:
        records: A list of records to normalize.

    Returns:
        A list of normalized records.
    """
    return [
        {
            "key": r.get("key", ""),
            "mt": r.get("mt", 0),
            "t1": r.get("t1", 0),
            "t2": r.get("t2", 0),
            "ds": r.get("ds", ""),
            "st": r.get("st", 0),
        }
        for r in records
    ]


def _post_process_records(
    records: list[Record],
    *,
    include_hidden: bool = False,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_by: Literal["t1", "t2", "st", "mt", "ds"] = "t2",
    sort_reverse: bool = True,
) -> list[Record]:
    """
    Post-process records after fetching them from the API.

    This includes sorting, filtering by tags, and manage hidden records.

    Args:
        records: A list of records to post-process.
        include_hidden: Whether to include hidden (i.e. deleted) records. Defaults to False.
        tags: A list of tags to filter records by. Defaults to None.
        tags_match: The mode to match tags. Can be "any" or "all". Defaults to "any".
        sort_by: The field to sort the records by. Can be "t1", "t2", "st", "mt", or "ds". Defaults to "t2".
        sort_reverse: Whether to sort in reverse order. Defaults to True.

    Returns:
        A list of post-processed records.
    """
    records = _normalize_records(records)
    records.sort(key=lambda r: r[sort_by], reverse=sort_reverse)
    if tags:
        match_func = any if tags_match == "any" else all
        records = [r for r in records if match_func(tag in r["ds"] for tag in tags)]
    if not include_hidden:
        records = [r for r in records if not r["ds"].startswith("HIDDEN")]
    return records


def get_records(
    start: int | datetime,
    end: int | datetime,
    *,
    include_partial_match: bool = True,
    include_hidden: bool = False,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_by: Literal["t1", "t2", "st", "mt", "ds"] = "t2",
    sort_reverse: bool = True,
) -> GetRecordsResponse:
    """
    Calls TimeTagger API using `GET /records?timerange={start}-{end}` and returns the response.

    Args:
        start: The start timestamp to get records from.
        end: The end timestamp to get records until.
        include_partial: Whether to include partial matches, i.e. records that are not fully contained in the range. Defaults to True.
        include_hidden: Whether to include hidden (i.e. deleted) records. Defaults to False.
        tags: A list of tags to filter records by. Defaults to None.
        tags_match: The mode to match tags. Can be "any" or "all". Defaults to "any".

    Returns:
        A dictionary containing the records from the API.
    """
    if isinstance(start, datetime):
        start = int(start.timestamp())
    if isinstance(end, datetime):
        end = int(end.timestamp())

    t1 = min(start, end) if include_partial_match else max(start, end)
    t2 = max(start, end) if include_partial_match else min(start, end)
    response = _request("GET", f"records?timerange={t1}-{t2}")

    response["records"] = _post_process_records(
        response["records"],
        include_hidden=include_hidden,
        tags=tags,
        tags_match=tags_match,
        sort_by=sort_by,
        sort_reverse=sort_reverse,
    )

    return cast(GetRecordsResponse, response)


def get_runnning_records(
    *,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_by: Literal["t1", "t2", "st", "mt", "ds"] = "t2",
    sort_reverse: bool = True,
) -> GetRecordsResponse:
    """
    Calls TimeTagger API to get currently running records.

    This searches for records who's timerange matches (roughly) the current time.
    The range is set to +/-35 minutes, to account for time drift between the server and client.

    Args:
        tags: A list of tags to filter records by. Defaults to None.
        tags_match: The mode to match tags. Can be "any" or "all". Defaults to "any".
        sort_by: The field to sort the records by. Can be "t1", "t2", "st", "mt", or "ds". Defaults to "t2".
        sort_reverse: Whether to sort in reverse order. Defaults to True.

    Returns:
        A dictionary containing the running records from the API.
    """
    now = int(time())
    start = now - 60 * 60 * 24
    end = now + 60 * 60 * 24
    response = get_records(start, end, tags=tags, tags_match=tags_match, sort_by=sort_by, sort_reverse=sort_reverse)
    response["records"] = [r for r in response["records"] if r["t1"] == r["t2"]]
    return response


def put_records(records: list[Record]) -> PutRecordsResponse:
    """
    Calls TimeTagger API using `PUT /records` and returns response.

    Args:
        records: A list of records to put.

    Returns:
        A dictionary containing the response from the API.
    """
    response = _request("PUT", "records", records)
    return cast(PutRecordsResponse, response)


def get_settings(settings: list[Settings]) -> GetSettingsResponse:
    """
    Calls TimeTagger API using `GET /settings` and returns the response.

    Returns:
        A dictionary containing the settings from the API.
    """
    response = _request("GET", "settings", settings)
    return cast(GetSettingsResponse, response)


def put_settings(settings: dict) -> PutSettingsResponse:
    """
    Calls TimeTagger API using `PUT /settings` and returns response.

    Args:
        settings: A dictionary containing the settings to put.

    Returns:
        A dictionary containing the response from the API.
    """
    response = _request("PUT", "settings", settings)
    return cast(PutSettingsResponse, response)


def get_updates(
    since: int = 0,
    *,
    include_hidden: bool = False,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_by: Literal["t1", "t2", "st", "mt", "ds"] = "t2",
    sort_reverse: bool = True,
) -> GetUpdatesResponse:
    """
    Calls TimeTagger API using `GET /updates?since={since}` and returns the response.

    Args:
        since: The timestamp to get updates since. Defaults to 0. Should typically use the last call's `server_time` value.
        include_hidden: Whether to include hidden (i.e. deleted) records. Defaults to False.
        tags: A list of tags to filter records by. Defaults to None.
        tags_match: The mode to match tags. Can be "any" or "all". Defaults to "any".
        sort_by: The field to sort the records by. Can be "t1", "t2", "st", "mt", or "ds". Defaults to "t2".
        sort_reverse: Whether to sort in reverse order. Defaults to True.

    Returns:
        A dictionary containing the updates from the API.
    """
    response = _request("GET", f"updates?since={since}")

    response["records"] = _post_process_records(
        response["records"],
        include_hidden=include_hidden,
        tags=tags,
        tags_match=tags_match,
        sort_by=sort_by,
        sort_reverse=sort_reverse,
    )

    return cast(GetRecordsResponse, response)


def continuous_updates(since: int = 0, delay: int = 2) -> Generator[GetUpdatesResponse, None]:
    """
    Generator that continually polls TimeTagger API using `GET /updates?since={since}`, using the last call's `server_time` value as the new `since` value.

    This allows continuous monitoring of server updates.

    Args:
        since: The timestamp to get updates since. Defaults to 0. Should typically use the last call's `server_time` value.
        delay: The minimul delay in seconds between requests. Defaults to 2 second.

    Yields:
        A dictionary containing the updates from the API.
    """

    while True:
        response = get_updates(since)
        since = response["server_time"]
        yield response
        sleep(delay)
