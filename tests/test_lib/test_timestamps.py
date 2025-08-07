"""Tests for timestamp utility functions."""

import time
from unittest.mock import patch

import pytest

from better_timetagger_cli.lib.timestamps import now_timestamp, round_timestamp


def test_now_timestamp_returns_integer():
    """Return current timestamp as integer."""
    result = now_timestamp()

    assert isinstance(result, int)
    # Should be a reasonable Unix timestamp (after year 2000)
    assert result > 946684800  # January 1, 2000


def test_now_timestamp_approximates_current_time():
    """Return timestamp close to current time."""
    expected = int(time.time())
    result = now_timestamp()

    # Should be within 1 second of expected time
    assert abs(result - expected) <= 1


@patch("better_timetagger_cli.lib.timestamps.time")
def test_now_timestamp_mocked(mock_time):
    """Return timestamp from mocked time.time()."""
    mock_time.return_value = 1640995200.0  # 2022-01-01 00:00:00 UTC

    result = now_timestamp()

    assert result == 1640995200
    mock_time.assert_called_once()


def test_round_timestamp_to_minutes():
    """Round timestamp to specified minute intervals."""
    timestamp = 1640995320  # 2022-01-01 00:02:00 UTC

    # Round to 5-minute intervals
    result = round_timestamp(timestamp, 5)
    expected = 1640995200  # 2022-01-01 00:00:00 UTC (rounded down)
    assert result == expected

    # Round to 15-minute intervals
    result = round_timestamp(timestamp, 15)
    expected = 1640995200  # 2022-01-01 00:00:00 UTC (rounded down)
    assert result == expected


def test_round_timestamp_rounds_up():
    """Round timestamp up when closer to next interval."""
    timestamp = 1640995500  # 2022-01-01 00:05:00 UTC

    # Round to 10-minute intervals - should round to 00:00:00
    result = round_timestamp(timestamp, 10)
    expected = 1640995200  # 2022-01-01 00:00:00 UTC
    assert result == expected

    # Test rounding up
    timestamp = 1640995800  # 2022-01-01 00:10:00 UTC
    result = round_timestamp(timestamp, 15)
    expected = 1640996100  # 2022-01-01 00:15:00 UTC (rounded up)
    assert result == expected


def test_round_timestamp_exact_intervals():
    """Handle timestamps that are exactly on interval boundaries."""
    timestamp = 1640995200  # 2022-01-01 00:00:00 UTC (exact hour)

    # Should return same timestamp when already on boundary
    result = round_timestamp(timestamp, 60)  # 1-hour intervals
    assert result == timestamp

    result = round_timestamp(timestamp, 15)  # 15-minute intervals
    assert result == timestamp


def test_round_timestamp_float_input():
    """Handle float timestamp input."""
    timestamp = 1640995320.5  # 2022-01-01 00:02:00.5 UTC

    result = round_timestamp(timestamp, 5)
    expected = 1640995200  # 2022-01-01 00:00:00 UTC
    assert result == expected
    assert isinstance(result, int)


def test_round_timestamp_various_intervals():
    """Round to various minute intervals correctly."""
    base_timestamp = 1640995200  # 2022-01-01 00:00:00 UTC

    test_cases = [
        (base_timestamp + 150, 1, base_timestamp + 120),  # 2.5 min → 2 min (1-min intervals)
        (base_timestamp + 450, 5, base_timestamp + 600),  # 7.5 min → 10 min (5-min intervals)
        (base_timestamp + 1050, 15, base_timestamp + 900),  # 17.5 min → 15 min (15-min intervals)
        (base_timestamp + 2700, 30, base_timestamp + 3600),  # 45 min → 60 min (30-min intervals)
    ]

    for timestamp, interval, expected in test_cases:
        result = round_timestamp(timestamp, interval)
        assert result == expected, f"Failed for timestamp {timestamp}, interval {interval}"


def test_round_timestamp_large_intervals():
    """Handle large rounding intervals."""
    timestamp = 1640995200  # 2022-01-01 00:00:00 UTC

    # Round to 2-hour intervals (120 minutes)
    result = round_timestamp(timestamp + 3900, 120)  # Add 65 minutes
    expected = timestamp + 7200  # Should round to next 2-hour boundary (120 minutes)
    assert result == expected


def test_round_timestamp_zero_interval():
    """Handle zero interval (edge case)."""
    timestamp = 1640995200

    with pytest.raises(ZeroDivisionError):
        round_timestamp(timestamp, 0)


def test_round_timestamp_negative_interval():
    """Handle negative interval."""
    timestamp = 1640995200

    # Negative intervals should still work mathematically
    result = round_timestamp(timestamp, -5)
    assert isinstance(result, int)


def test_round_timestamp_negative_timestamp():
    """Handle negative timestamp (pre-1970)."""
    timestamp = -86400  # 1969-12-31 00:00:00 UTC

    result = round_timestamp(timestamp, 60)
    assert isinstance(result, int)
    # Should handle negative timestamps correctly
    expected = -86400  # Already on hour boundary
    assert result == expected


def test_round_timestamp_returns_integer():
    """Always return integer even with float inputs."""
    test_cases = [
        (1640995320.7, 5),
        (1640995320.2, 15),
        (1640995320.0, 30),
    ]

    for timestamp, interval in test_cases:
        result = round_timestamp(timestamp, interval)
        assert isinstance(result, int)
