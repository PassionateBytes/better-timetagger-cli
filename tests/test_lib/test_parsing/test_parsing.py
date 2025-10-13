"""Tests for input parsing and validation functions."""

import time
from datetime import datetime

import pytest

from better_timetagger_cli.lib.parsing import (
    parse_at,
    parse_datetime,
    parse_start_end,
    tags_callback,
)


# Tests for tags_callback
def test_tags_callback_adds_hash_prefix(mock_click_context, mock_click_param):
    """Add '#' prefix to tags without it."""
    tags = ["work", "urgent", "project"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert result == ["#work", "#urgent", "#project"] or set(result) == {"#work", "#urgent", "#project"}
    assert all(tag.startswith("#") for tag in result)


def test_tags_callback_preserves_existing_hash(mock_click_context, mock_click_param):
    """Preserve tags that already have '#' prefix."""
    tags = ["#work", "#urgent", "#project"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert set(result) == {"#work", "#urgent", "#project"}


def test_tags_callback_mixed_tags(mock_click_context, mock_click_param):
    """Handle mix of tags with and without '#' prefix."""
    tags = ["work", "#urgent", "project", "#meeting"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert set(result) == {"#work", "#urgent", "#project", "#meeting"}


def test_tags_callback_removes_duplicates(mock_click_context, mock_click_param):
    """Remove duplicate tags."""
    tags = ["work", "work", "#work", "project", "#project"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert set(result) == {"#work", "#project"}
    assert len(result) == 2


def test_tags_callback_empty_list(mock_click_context, mock_click_param):
    """Handle empty tag list."""
    result = tags_callback(mock_click_context, mock_click_param, [])

    assert result == []


def test_tags_callback_single_tag(mock_click_context, mock_click_param):
    """Handle single tag."""
    result = tags_callback(mock_click_context, mock_click_param, ["work"])

    assert result == ["#work"]


def test_tags_callback_special_characters(mock_click_context, mock_click_param):
    """Handle tags with special characters."""
    tags = ["work-from-home", "project/2024", "urgent!", "team@office"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert all(tag.startswith("#") for tag in result)
    assert len(result) == 4


# Tests for parse_datetime with real parsedatetime
def test_parse_datetime_date_only():
    """Parse date-only input."""
    # This test uses real parsedatetime
    result = parse_datetime("2024-03-15")

    assert result.year == 2024
    assert result.month == 3
    assert result.day == 15
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0


def test_parse_datetime_with_mock_date_only(mock_parsedatetime):
    """Parse date-only input (hasDate=True, hasTime=False) sets time to 00:00:00."""
    parsed_time = time.struct_time((2024, 3, 15, 14, 30, 0, 0, 0, 0))
    mock_parsedatetime.set_result("March 15, 2024", parsed_time, has_date=True, has_time=False)

    result = parse_datetime("March 15, 2024")

    assert result == datetime(2024, 3, 15, 0, 0, 0)


def test_parse_datetime_with_mock_time_only(mock_parsedatetime, mock_datetime_today):
    """Parse time-only input (hasDate=False, hasTime=True) uses today's date."""
    parsed_time = time.struct_time((2020, 1, 1, 14, 30, 0, 0, 0, 0))
    mock_parsedatetime.set_result("2:30 PM", parsed_time, has_date=False, has_time=True)

    result = parse_datetime("2:30 PM")

    # Should use today's date (2024-03-15) with parsed time
    assert result == datetime(2024, 3, 15, 14, 30, 0)


def test_parse_datetime_with_mock_date_and_time(mock_parsedatetime):
    """Parse date and time input (hasDate=True, hasTime=True)."""
    parsed_time = time.struct_time((2024, 3, 15, 14, 30, 45, 0, 0, 0))
    mock_parsedatetime.set_result("March 15, 2024 at 2:30:45 PM", parsed_time, has_date=True, has_time=True)

    result = parse_datetime("March 15, 2024 at 2:30:45 PM")

    assert result == datetime(2024, 3, 15, 14, 30, 45)


def test_parse_datetime_failed_parse(mock_parsedatetime, mock_abort):
    """Abort when parsing fails (hasDate=False, hasTime=False)."""
    mock_parsedatetime.set_result("gibberish", None, has_date=False, has_time=False)

    with pytest.raises(SystemExit):
        parse_datetime("gibberish")

    assert mock_abort["called"]
    assert "Could not parse input: gibberish" in mock_abort["message"]


def test_parse_datetime_natural_language_inputs():
    """Parse various natural language inputs using real parsedatetime."""
    # Test relative dates
    today = datetime.today()

    # These tests use real parsedatetime library
    result = parse_datetime("today")
    assert result.date() == today.date()

    result = parse_datetime("now")
    assert result.date() == today.date()
    # Time should be close to current time (within a few seconds)
    assert abs((result - datetime.now()).total_seconds()) < 5


# Tests for parse_start_end
def test_parse_start_end_both_provided(mock_parsedatetime):
    """Parse both start and end dates."""
    # Set up mock results
    start_time = time.struct_time((2024, 1, 1, 0, 0, 0, 0, 0, 0))
    end_time = time.struct_time((2024, 12, 31, 23, 59, 59, 0, 0, 0))
    mock_parsedatetime.set_result("January 1, 2024", start_time, has_date=True, has_time=False)
    mock_parsedatetime.set_result("December 31, 2024", end_time, has_date=True, has_time=True)

    start_dt, end_dt = parse_start_end("January 1, 2024", "December 31, 2024")

    assert start_dt == datetime(2024, 1, 1, 0, 0, 0)
    assert end_dt == datetime(2024, 12, 31, 23, 59, 59)


def test_parse_start_end_only_start():
    """Use default end date when only start is provided."""
    start_dt, end_dt = parse_start_end("2024-01-01", None)

    assert start_dt.year == 2024
    assert start_dt.month == 1
    assert start_dt.day == 1
    assert end_dt == datetime(3000, 1, 1)


def test_parse_start_end_only_end():
    """Use default start date when only end is provided."""
    start_dt, end_dt = parse_start_end(None, "2024-12-31")

    assert start_dt == datetime(2000, 1, 1)
    assert end_dt.year == 2024
    assert end_dt.month == 12
    assert end_dt.day == 31


def test_parse_start_end_neither_provided():
    """Use default dates when neither start nor end provided."""
    start_dt, end_dt = parse_start_end(None, None)

    assert start_dt == datetime(2000, 1, 1)
    assert end_dt == datetime(3000, 1, 1)


def test_parse_start_end_empty_strings():
    """Handle empty strings as None."""
    start_dt, end_dt = parse_start_end("", "")

    assert start_dt == datetime(2000, 1, 1)
    assert end_dt == datetime(3000, 1, 1)


def test_parse_start_end_invalid_input(mock_parsedatetime, mock_abort):
    """Abort when parsing invalid input."""
    mock_parsedatetime.set_result("invalid", None, has_date=False, has_time=False)

    with pytest.raises(SystemExit):
        parse_start_end("invalid", None)

    assert mock_abort["called"]


# Tests for parse_at
def test_parse_at_valid_input(mock_parsedatetime):
    """Parse valid 'at' parameter to timestamp."""
    at_time = time.struct_time((2024, 3, 15, 14, 30, 0, 0, 0, 0))
    mock_parsedatetime.set_result("March 15, 2024 2:30 PM", at_time, has_date=True, has_time=True)

    result = parse_at("March 15, 2024 2:30 PM")

    expected_dt = datetime(2024, 3, 15, 14, 30, 0)
    assert result == int(expected_dt.timestamp())


def test_parse_at_none_input():
    """Return None when 'at' parameter is None."""
    result = parse_at(None)

    assert result is None


def test_parse_at_empty_string():
    """Return None when 'at' parameter is empty string."""
    result = parse_at("")

    assert result is None


def test_parse_at_natural_language():
    """Parse natural language 'at' parameter."""
    # This uses real parsedatetime
    result = parse_at("yesterday at 3pm")

    assert isinstance(result, int)
    assert result > 0


def test_parse_at_invalid_input(mock_parsedatetime, mock_abort):
    """Abort when parsing invalid 'at' input."""
    mock_parsedatetime.set_result("invalid time", None, has_date=False, has_time=False)

    with pytest.raises(SystemExit):
        parse_at("invalid time")

    assert mock_abort["called"]
    assert "Could not parse input: invalid time" in mock_abort["message"]


def test_parse_at_returns_integer_timestamp():
    """Ensure parse_at returns integer timestamp."""
    result = parse_at("2024-03-15 14:30:00")

    assert isinstance(result, int)
    # Verify it's a reasonable Unix timestamp (after year 2000)
    assert result > 946684800  # January 1, 2000


# Edge cases and integration tests
def test_parse_datetime_various_formats():
    """Test various date/time formats with real parsedatetime."""
    formats = [
        "3/15/2024",
        "15-Mar-2024",
        "March 15th, 2024",
        "15:30",
        "3:30 PM",
        "tomorrow",
        "next week",
        "last month",
    ]

    for fmt in formats:
        result = parse_datetime(fmt)
        assert isinstance(result, datetime)


def test_parse_functions_with_whitespace(mock_parsedatetime):
    """Handle inputs with extra whitespace."""
    at_time = time.struct_time((2024, 3, 15, 14, 30, 0, 0, 0, 0))
    mock_parsedatetime.set_result("  March 15, 2024  ", at_time, has_date=True, has_time=False)

    result = parse_datetime("  March 15, 2024  ")
    assert result.year == 2024

    # parse_at should handle whitespace too
    mock_parsedatetime.set_result("  2:30 PM  ", at_time, has_date=False, has_time=True)
    result = parse_at("  2:30 PM  ")
    assert isinstance(result, int)


def test_tags_callback_unicode_tags(mock_click_context, mock_click_param):
    """Handle Unicode characters in tags."""
    tags = ["工作", "urgent", "プロジェクト", "café"]
    result = tags_callback(mock_click_context, mock_click_param, tags)

    assert all(tag.startswith("#") for tag in result)
    assert set(result) == {"#工作", "#urgent", "#プロジェクト", "#café"}
