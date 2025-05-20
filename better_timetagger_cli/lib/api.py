import json
from typing import Literal, cast

import click
import requests

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

    config = load_config()
    url = config["api_url"].rstrip("/") + "/" + path.lstrip("/")
    token = config["api_token"].strip()
    ssl_verify = config["ssl_verify"]

    headers = {"authtoken": token}
    response = requests.request(method.upper(), url, json=body, headers=headers, verify=ssl_verify)

    if response.status_code == 200:
        return response.json()
    else:
        response_text = response.text
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            pass
        raise click.Abort(f"API request failed with status code: {response.status_code}\n{response_text}")


def get_records(start: int, end: int, include_partial_match: True) -> GetRecordsResponse:
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
    response = _request("GET", f"updates?timerange={timestamp_1}-{timestamp_2}")
    return cast(GetRecordsResponse, response)


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
