"""Tests for API communication functions."""

from datetime import datetime
from unittest.mock import patch

from better_timetagger_cli.lib.api import get_records, put_records
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


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_records_converts_datetime_to_timestamp(mock_api_request):
    """Convert datetime objects to integer timestamps."""
    mock_api_request.return_value = {"records": []}

    start = datetime(2022, 1, 1, 0, 0, 0)
    end = datetime(2022, 1, 2, 0, 0, 0)
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    get_records(start, end)

    # Extract the URL path from the call
    call_args = mock_api_request.call_args[0]
    assert call_args[0] == "GET"
    assert f"timerange={start_ts}-{end_ts}" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_records_uses_integer_timestamps_directly(mock_api_request):
    """Use integer timestamps directly without conversion."""
    mock_api_request.return_value = {"records": []}

    start = 1640995200
    end = 1641081600

    get_records(start, end)

    call_args = mock_api_request.call_args[0]
    assert "timerange=1640995200-1641081600" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_records_partial_match_uses_min_max(mock_api_request):
    """With partial match, use min as t1 and max as t2."""
    mock_api_request.return_value = {"records": []}

    start = 1641081600
    end = 1640995200

    get_records(start, end, include_partial_match=True)

    # With partial match: t1=min(start,end), t2=max(start,end)
    call_args = mock_api_request.call_args[0]
    assert "timerange=1640995200-1641081600" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_records_no_partial_match_uses_max_min(mock_api_request):
    """Without partial match, swap min/max (use max as t1 and min as t2)."""
    mock_api_request.return_value = {"records": []}

    start = 1640995200
    end = 1641081600

    get_records(start, end, include_partial_match=False)

    # Without partial match: t1=max(start,end), t2=min(start,end)
    call_args = mock_api_request.call_args[0]
    assert "timerange=1641081600-1640995200" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_records_returns_response_with_records(mock_api_request):
    """Return response containing processed records."""
    mock_api_request.return_value = {
        "records": [
            {
                "key": "key1",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640995800,
                "ds": "#work",
                "st": 1640995200.0,
            }
        ]
    }

    result = get_records(1640995200, 1641081600)

    assert "records" in result
    assert len(result["records"]) == 1
