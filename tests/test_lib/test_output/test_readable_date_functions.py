"""Tests for readable_date_time and readable_weekday functions."""

from datetime import datetime

import pytest

from better_timetagger_cli.lib.output import readable_date_time, readable_weekday


@pytest.fixture
def mock_config(monkeypatch):
    """Mock get_config to return known date formats."""

    def _mock_config(datetime_format="%Y-%m-%d %H:%M", weekday_format="%a"):
        def get_config():
            return {
                "datetime_format": datetime_format,
                "weekday_format": weekday_format,
            }

        monkeypatch.setattr("better_timetagger_cli.lib.config.get_config", get_config)

    return _mock_config


def test_readable_date_time_with_timestamp(mock_config):
    """Format timestamp as readable date and time."""
    mock_config(datetime_format="%Y-%m-%d %H:%M")
    timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
    result = readable_date_time(timestamp)
    assert "2021-01-01" in result
    assert ":" in result  # Has time component


def test_readable_date_time_with_datetime(mock_config):
    """Format datetime object as readable date and time."""
    mock_config(datetime_format="%Y-%m-%d")
    dt = datetime(2021, 6, 15, 14, 30)
    result = readable_date_time(dt)
    assert result == "2021-06-15"


def test_readable_date_time_custom_format(mock_config):
    """Use custom date format from config."""
    mock_config(datetime_format="%d/%m/%Y")
    timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
    result = readable_date_time(timestamp)
    assert "01/01/2021" in result


def test_readable_weekday_with_timestamp(mock_config):
    """Format timestamp weekday."""
    mock_config(weekday_format="%a")
    timestamp = 1609459200  # 2021-01-01 (Friday) 00:00:00 UTC
    result = readable_weekday(timestamp)
    assert result == "Fri"


def test_readable_weekday_with_datetime(mock_config):
    """Format datetime weekday."""
    mock_config(weekday_format="%a")
    dt = datetime(2021, 1, 1)  # Friday
    result = readable_weekday(dt)
    assert result == "Fri"


def test_readable_weekday_full_name(mock_config):
    """Use full weekday name format."""
    mock_config(weekday_format="%A")
    dt = datetime(2021, 1, 1)  # Friday
    result = readable_weekday(dt)
    assert result == "Friday"
