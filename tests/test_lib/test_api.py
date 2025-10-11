"""Tests for API communication functions."""

from unittest.mock import patch

from better_timetagger_cli.lib.api import put_records
from better_timetagger_cli.lib.types import Record


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_records_flattens_single_record(mock_api_request):
    """Flatten and send a single record."""
    mock_api_request.return_value = {"accepted": ["key1"], "failed": [], "errors": []}

    record: Record = {
        "key": "key1",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640995800,
        "ds": "#work",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 600,
    }

    result = put_records(record)

    mock_api_request.assert_called_once_with("PUT", "records", [record])
    assert result["accepted"] == ["key1"]


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_records_flattens_multiple_records(mock_api_request):
    """Flatten and send multiple records."""
    mock_api_request.return_value = {
        "accepted": ["key1", "key2"],
        "failed": [],
        "errors": [],
    }

    record1: Record = {
        "key": "key1",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640995800,
        "ds": "#work",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 600,
    }

    record2: Record = {
        "key": "key2",
        "mt": 1640995200,
        "t1": 1640995800,
        "t2": 1640996100,
        "ds": "#meeting",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 300,
    }

    result = put_records(record1, record2)

    mock_api_request.assert_called_once_with("PUT", "records", [record1, record2])
    assert result["accepted"] == ["key1", "key2"]


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_records_flattens_list_of_records(mock_api_request):
    """Flatten a list of records passed as a single argument."""
    mock_api_request.return_value = {
        "accepted": ["key1", "key2"],
        "failed": [],
        "errors": [],
    }

    records: list[Record] = [
        {
            "key": "key1",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "key2",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996100,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    result = put_records(records)

    mock_api_request.assert_called_once_with("PUT", "records", records)
    assert result["accepted"] == ["key1", "key2"]


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_records_flattens_mixed_arguments(mock_api_request):
    """Flatten mixed individual records and lists."""
    mock_api_request.return_value = {
        "accepted": ["key1", "key2", "key3"],
        "failed": [],
        "errors": [],
    }

    record1: Record = {
        "key": "key1",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640995800,
        "ds": "#work",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 600,
    }

    records_list: list[Record] = [
        {
            "key": "key2",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996100,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
        {
            "key": "key3",
            "mt": 1640995200,
            "t1": 1640996100,
            "t2": 1640996400,
            "ds": "#review",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    result = put_records(record1, records_list)

    expected_flattened = [record1, records_list[0], records_list[1]]
    mock_api_request.assert_called_once_with("PUT", "records", expected_flattened)
    assert result["accepted"] == ["key1", "key2", "key3"]
