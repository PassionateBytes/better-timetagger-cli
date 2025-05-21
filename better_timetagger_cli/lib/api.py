import json
from collections.abc import Generator
from time import sleep, time
from typing import Literal, cast

import click
import requests
from rich import print

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
        print(f"[red]API request failed: {e.__class__.__name__}[/red]\n[dim red]{e}[/dim red]")
        raise click.Abort from e

    if response.status_code != 200:
        response_text = response.text
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            pass
        print(f"[red]API request failed with status code: {response.status_code}[/red]\n[dim red]{response_text}[/dim red]")
        raise click.Abort

    return response.json()


def get_records(start: int, end: int, include_partial_match: bool = True) -> GetRecordsResponse:
    """
    Calls TimeTagger API using `GET /records?timerange={start}-{end}` and returns the response.

    Args:
        start: The start timestamp to get records from.
        end: The end timestamp to get records until.
        include_partial: Whether to include partial matches, i.e. records that are not fully contained in the range. Defaults to True.

    Returns:
        A dictionary containing the records from the API.
    """
    timestamp_1 = min(start, end) if include_partial_match else max(start, end)
    timestamp_2 = max(start, end) if include_partial_match else min(start, end)
    response = _request("GET", f"records?timerange={timestamp_1}-{timestamp_2}")
    return cast(GetRecordsResponse, response)


def get_runnning_records() -> GetRecordsResponse:
    """
    Calls TimeTagger API to get currently running records.

    This searches for records who's timerange matches (roughly) the current time.
    The range is set to +/-35 minutes, to account for time drift between the server and client.

    Returns:
        A dictionary containing the running records from the API.
    """
    now = int(time())
    t1 = now - 35 * 60
    t2 = now + 35 * 60
    response = get_records(t1, t2)
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


def get_updates(since: int = 0) -> GetUpdatesResponse:
    """
    Calls TimeTagger API using `GET /updates?since={since}` and returns the response.

    Args:
        since: The timestamp to get updates since. Defaults to 0. Should typically use the last call's `server_time` value.

    Returns:
        A dictionary containing the updates from the API.
    """
    response = _request("GET", f"updates?since={since}")
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
