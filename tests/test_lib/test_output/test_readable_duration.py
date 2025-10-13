"""Tests for the readable_duration function."""

from datetime import timedelta

from better_timetagger_cli.lib.output import readable_duration


def test_hours_and_minutes():
    """Format duration with both hours and minutes."""
    result = readable_duration(3661)  # 1 hour, 1 minute, 1 second
    assert result == "1h  1m"


def test_multiple_hours_and_minutes():
    """Format duration with multiple hours and minutes."""
    result = readable_duration(9000)  # 2 hours, 30 minutes
    assert result == "2h 30m"


def test_only_minutes():
    """Format duration with only minutes (no hours)."""
    result = readable_duration(1800)  # 30 minutes
    assert result == "30m"


def test_single_minute():
    """Format duration with single minute."""
    result = readable_duration(60)  # 1 minute
    assert result == "1m"


def test_zero_duration():
    """Format zero duration."""
    result = readable_duration(0)
    assert result == "0m"


def test_with_timedelta():
    """Accept timedelta as input."""
    result = readable_duration(timedelta(hours=2, minutes=15))
    assert result == "2.0h 15.0m"


def test_with_float():
    """Accept float as input."""
    result = readable_duration(3661.5)  # 1 hour, 1 minute, 1.5 seconds
    assert result == "1.0h 1.0m"


def test_large_duration():
    """Format large duration (multiple days)."""
    result = readable_duration(86400 + 3600)  # 1 day + 1 hour = 25 hours
    assert result == "25h  0m"


def test_rounds_down_seconds():
    """Seconds are discarded (not rounded up)."""
    result = readable_duration(3659)  # 1 hour, 59 seconds
    assert result == "1h  0m"


def test_less_than_minute():
    """Duration less than a minute."""
    result = readable_duration(30)  # 30 seconds
    assert result == "0m"
