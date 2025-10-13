"""Tests for the print_records function."""

from unittest.mock import patch

from better_timetagger_cli.lib.output import print_records
from better_timetagger_cli.lib.types import Record


def test_print_records_calls_console_print():
    """Test that print_records calls console.print with rendered table."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    with patch("better_timetagger_cli.lib.output.console") as mock_console:
        print_records(records)
        mock_console.print.assert_called_once()


def test_print_records_with_show_index():
    """Test print_records with show_index parameter."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    with patch("better_timetagger_cli.lib.output.console") as mock_console:
        print_records(records, show_index=True)
        mock_console.print.assert_called_once()


def test_print_records_with_show_keys():
    """Test print_records with show_keys parameter."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    with patch("better_timetagger_cli.lib.output.console") as mock_console:
        print_records(records, show_keys=True)
        mock_console.print.assert_called_once()


def test_print_records_with_record_status():
    """Test print_records with record_status parameter."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        }
    ]

    with patch("better_timetagger_cli.lib.output.console") as mock_console:
        print_records(records, record_status={"abc123": "modified"})
        mock_console.print.assert_called_once()
