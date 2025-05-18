from typing import Literal

import click
import requests

from .config import load_config


def request(
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
        raise click.Abort(f"API request failed with status code {response.status_code}!\n{response.text}")
