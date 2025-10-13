"""Tests for API communication functions."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from better_timetagger_cli.lib.api import (
    api_request,
    continuous_updates,
    get_records,
    get_running_records,
    get_settings,
    get_updates,
    put_records,
    put_settings,
)
from better_timetagger_cli.lib.types import Record, Settings


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


@patch("better_timetagger_cli.lib.api.get_updates")
@patch("better_timetagger_cli.lib.api.get_config")
def test_get_running_records_calls_get_updates_when_search_window_disabled(mock_get_config, mock_get_updates):
    """Call get_updates when search window is negative (disabled)."""
    mock_get_config.return_value = {"running_records_search_window": -1}
    mock_get_updates.return_value = {"records": []}

    result = get_running_records(tags=["#work"], tags_match="all")

    mock_get_updates.assert_called_once_with(
        tags=["#work"],
        tags_match="all",
        sort_by="t2",
        sort_reverse=True,
        hidden=False,
        running=True,
    )
    assert "records" in result


@patch("better_timetagger_cli.lib.api.get_records")
@patch("better_timetagger_cli.lib.api.get_config")
@patch("better_timetagger_cli.lib.api.datetime")
def test_get_running_records_calls_get_records_when_search_window_enabled(mock_datetime, mock_get_config, mock_get_records):
    """Call get_records with time window when search window is enabled."""
    mock_get_config.return_value = {"running_records_search_window": 2}
    mock_get_records.return_value = {"records": []}

    # Mock datetime.now() to return a fixed time
    fixed_now = datetime(2022, 1, 15, 12, 0, 0)
    mock_datetime.now.return_value = fixed_now
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    result = get_running_records()

    # Should call get_records with start=now-2weeks, end=now+1day
    assert mock_get_records.call_count == 1
    call_kwargs = mock_get_records.call_args[1]
    assert call_kwargs["include_partial_match"] is True
    assert call_kwargs["running"] is True
    assert "records" in result


@patch("better_timetagger_cli.lib.api.get_records")
@patch("better_timetagger_cli.lib.api.get_config")
def test_get_running_records_passes_filter_parameters(mock_get_config, mock_get_records):
    """Pass all filter parameters to underlying get_records call."""
    mock_get_config.return_value = {"running_records_search_window": 1}
    mock_get_records.return_value = {"records": []}

    get_running_records(
        tags=["#work", "#meeting"],
        tags_match="all",
        sort_by="t1",
        sort_reverse=False,
        hidden=True,
    )

    call_kwargs = mock_get_records.call_args[1]
    assert call_kwargs["tags"] == ["#work", "#meeting"]
    assert call_kwargs["tags_match"] == "all"
    assert call_kwargs["sort_by"] == "t1"
    assert call_kwargs["sort_reverse"] is False
    assert call_kwargs["hidden"] is True
    assert call_kwargs["running"] is True


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_updates_converts_datetime_to_timestamp(mock_api_request):
    """Convert datetime objects to integer timestamps."""
    mock_api_request.return_value = {"records": [], "settings": [], "server_time": 0, "reset": 0}

    since = datetime(2022, 1, 1, 0, 0, 0)
    since_ts = int(since.timestamp())

    get_updates(since)

    call_args = mock_api_request.call_args[0]
    assert call_args[0] == "GET"
    assert f"updates?since={since_ts}" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_updates_uses_integer_timestamp_directly(mock_api_request):
    """Use integer timestamps directly without conversion."""
    mock_api_request.return_value = {"records": [], "settings": [], "server_time": 0, "reset": 0}

    get_updates(1640995200)

    call_args = mock_api_request.call_args[0]
    assert "updates?since=1640995200" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_updates_uses_default_since_value(mock_api_request):
    """Use default since value of 0 when not specified."""
    mock_api_request.return_value = {"records": [], "settings": [], "server_time": 0, "reset": 0}

    get_updates()

    call_args = mock_api_request.call_args[0]
    assert "updates?since=0" in call_args[1]


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_updates_returns_response_with_data(mock_api_request):
    """Return response containing processed records and settings."""
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
        ],
        "settings": [],
        "server_time": 1640995800,
        "reset": 0,
    }

    result = get_updates(1640995200)

    assert "records" in result
    assert len(result["records"]) == 1
    assert "settings" in result
    assert result["server_time"] == 1640995800
    assert result["reset"] == 0


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_settings_sends_settings_dict(mock_api_request):
    """Send settings dictionary via PUT request."""
    mock_api_request.return_value = {"accepted": ["setting1"], "failed": [], "errors": []}

    settings = {"setting1": "value1", "setting2": "value2"}
    result = put_settings(settings)

    mock_api_request.assert_called_once_with("PUT", "settings", settings)
    assert result["accepted"] == ["setting1"]


@patch("better_timetagger_cli.lib.api.api_request")
def test_put_settings_handles_empty_dict(mock_api_request):
    """Handle empty settings dictionary."""
    mock_api_request.return_value = {"accepted": [], "failed": [], "errors": []}

    result = put_settings({})

    mock_api_request.assert_called_once_with("PUT", "settings", {})
    assert result["accepted"] == []


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_settings_sends_settings_list(mock_api_request):
    """Send settings list via GET request."""
    mock_api_request.return_value = {
        "settings": [
            {
                "key": "setting1",
                "mt": 1640995200,
                "st": 1640995200,
                "value": "value1",
            }
        ]
    }

    settings: list[Settings] = [
        {
            "key": "setting1",
            "mt": 1640995200,
            "st": 1640995200,
            "value": "value1",
        }
    ]

    result = get_settings(settings)

    mock_api_request.assert_called_once_with("GET", "settings", settings)
    assert "settings" in result
    assert len(result["settings"]) == 1


@patch("better_timetagger_cli.lib.api.api_request")
def test_get_settings_handles_empty_list(mock_api_request):
    """Handle empty settings list."""
    mock_api_request.return_value = {"settings": []}

    result = get_settings([])

    mock_api_request.assert_called_once_with("GET", "settings", [])
    assert result["settings"] == []


@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_success(mock_get_config, mock_request):
    """Make successful API request and return JSON response."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "test_token",
        "ssl_verify": True,
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_request.return_value = mock_response

    result = api_request("GET", "test/path")

    assert result == {"data": "test"}
    mock_request.assert_called_once_with(
        "GET",
        "https://example.com/api/v2/test/path",
        json=None,
        headers={"authtoken": "test_token"},
        verify=True,
    )


@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_with_body(mock_get_config, mock_request):
    """Send request body as JSON."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "test_token",
        "ssl_verify": False,
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    body = {"key": "value"}
    result = api_request("POST", "endpoint", body)

    assert result == {"success": True}
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["json"] == body


@patch("better_timetagger_cli.lib.api.abort")
@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_handles_http_error(mock_get_config, mock_request, mock_abort):
    """Call abort on non-200 status code."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "test_token",
        "ssl_verify": True,
    }

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    mock_response.json.return_value = {"error": "Not found"}
    mock_request.return_value = mock_response
    mock_abort.side_effect = SystemExit(1)

    with pytest.raises(SystemExit):
        api_request("GET", "nonexistent")

    assert mock_abort.called
    abort_message = mock_abort.call_args[0][0]
    assert "404" in abort_message


@patch("better_timetagger_cli.lib.api.abort")
@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_handles_request_exception(mock_get_config, mock_request, mock_abort):
    """Call abort when request raises exception."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "test_token",
        "ssl_verify": True,
    }

    mock_request.side_effect = ConnectionError("Connection failed")
    mock_abort.side_effect = SystemExit(1)

    with pytest.raises(SystemExit):
        api_request("GET", "test")

    assert mock_abort.called
    abort_message = mock_abort.call_args[0][0]
    assert "ConnectionError" in abort_message


@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_strips_token_whitespace(mock_get_config, mock_request):
    """Strip whitespace from API token."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "  test_token  ",
        "ssl_verify": True,
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    api_request("GET", "test")

    headers = mock_request.call_args[1]["headers"]
    assert headers["authtoken"] == "test_token"


@patch("better_timetagger_cli.lib.api.requests.request")
@patch("better_timetagger_cli.lib.api.get_config")
def test_api_request_handles_leading_slash_in_path(mock_get_config, mock_request):
    """Remove leading slash from path."""
    mock_get_config.return_value = {
        "base_url": "https://example.com",
        "api_token": "test_token",
        "ssl_verify": True,
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    api_request("GET", "/test/path")

    url = mock_request.call_args[0][1]
    assert url == "https://example.com/api/v2/test/path"


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_yields_initial_response(mock_get_updates, mock_sleep):
    """Yield initial response from continuous_updates."""
    mock_get_updates.return_value = {
        "records": [
            {
                "key": "key1",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640995800,
                "ds": "#work",
                "st": 1640995200.0,
            }
        ],
        "settings": [],
        "server_time": 1640995800,
        "reset": 0,
    }

    generator = continuous_updates()
    result = next(generator)

    assert "records" in result
    assert len(result["records"]) == 1
    assert result["server_time"] == 1640995800
    # Sleep is called after yield, so hasn't been called yet
    assert mock_sleep.call_count == 0


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_uses_server_time_for_next_request(mock_get_updates, mock_sleep):
    """Use previous server_time as since parameter for next request."""
    mock_get_updates.side_effect = [
        {
            "records": [],
            "settings": [],
            "server_time": 1000,
            "reset": 0,
        },
        {
            "records": [],
            "settings": [],
            "server_time": 2000,
            "reset": 0,
        },
    ]

    generator = continuous_updates(since=0)
    next(generator)
    next(generator)

    # First call uses the provided since=0
    assert mock_get_updates.call_args_list[0][0][0] == 0
    # Second call uses server_time from first response
    assert mock_get_updates.call_args_list[1][0][0] == 1000


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_merges_records_when_not_reset(mock_get_updates, mock_sleep):
    """Merge new records with cached records when reset is False."""
    # First update has key1, second update has key2
    # Both should be merged in the cache
    mock_get_updates.side_effect = [
        {
            "records": [
                {
                    "key": "key1",
                    "mt": 1640995200,
                    "t1": 1640995200,
                    "t2": 1640995800,
                    "ds": "#work",
                    "st": 1640995200.0,
                }
            ],
            "settings": [],
            "server_time": 1000,
            "reset": 0,
        },
        {
            "records": [
                {
                    "key": "key2",
                    "mt": 1640995800,
                    "t1": 1640995800,
                    "t2": 1640996100,
                    "ds": "#meeting",
                    "st": 1640995800.0,
                }
            ],
            "settings": [],
            "server_time": 2000,
            "reset": 0,
        },
    ]

    generator = continuous_updates()
    first = next(generator)

    # First response has one record (key1)
    assert len(first["records"]) == 1
    record_keys = [r["key"] for r in first["records"]]
    assert "key1" in record_keys

    second = next(generator)

    # Second response merges both records (key1 + key2)
    assert len(second["records"]) == 2
    record_keys = [r["key"] for r in second["records"]]
    assert "key1" in record_keys
    assert "key2" in record_keys


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_replaces_cache_on_reset(mock_get_updates, mock_sleep):
    """Replace entire cache when reset is True."""
    mock_get_updates.side_effect = [
        {
            "records": [
                {
                    "key": "key1",
                    "mt": 1640995200,
                    "t1": 1640995200,
                    "t2": 1640995800,
                    "ds": "#work",
                    "st": 1640995200.0,
                }
            ],
            "settings": [],
            "server_time": 1000,
            "reset": 0,
        },
        {
            "records": [
                {
                    "key": "key2",
                    "mt": 1640995800,
                    "t1": 1640995800,
                    "t2": 1640996100,
                    "ds": "#meeting",
                    "st": 1640995800.0,
                }
            ],
            "settings": [],
            "server_time": 2000,
            "reset": 1,
        },
    ]

    generator = continuous_updates()
    first = next(generator)
    second = next(generator)

    # First response has one record
    assert len(first["records"]) == 1
    assert first["records"][0]["key"] == "key1"

    # Second response replaces cache due to reset
    assert len(second["records"]) == 1
    assert second["records"][0]["key"] == "key2"


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_uses_custom_delay(mock_get_updates, mock_sleep):
    """Use custom delay parameter for sleep."""
    mock_get_updates.return_value = {
        "records": [],
        "settings": [],
        "server_time": 1000,
        "reset": 0,
    }

    generator = continuous_updates(delay=10)
    next(generator)

    # Sleep happens after yield, so advance generator one more time
    try:
        next(generator)
    except StopIteration:  # pragma: no cover
        pass

    # Should have called sleep with custom delay
    assert mock_sleep.call_count >= 1
    mock_sleep.assert_any_call(10)


@patch("better_timetagger_cli.lib.api.sleep")
@patch("better_timetagger_cli.lib.api.get_updates")
def test_continuous_updates_filters_running_records(mock_get_updates, mock_sleep):
    """Filter for running records when running=True."""
    mock_get_updates.return_value = {
        "records": [
            {
                "key": "key1",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640995200,  # Running record (t1 == t2)
                "ds": "#work",
                "st": 1640995200.0,
            },
            {
                "key": "key2",
                "mt": 1640995200,
                "t1": 1640995200,
                "t2": 1640995800,  # Stopped record
                "ds": "#meeting",
                "st": 1640995200.0,
            },
        ],
        "settings": [],
        "server_time": 1000,
        "reset": 0,
    }

    generator = continuous_updates(running=True)
    result = next(generator)

    # Should only have the running record
    assert len(result["records"]) == 1
    assert result["records"][0]["key"] == "key1"
