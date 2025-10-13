"""Tests for the print_records_with_summary function."""

from unittest.mock import patch

from better_timetagger_cli.lib.output import print_records_with_summary
from better_timetagger_cli.lib.types import Record


def test_print_records_with_summary_calls_console_print():
    """Test that print_records_with_summary calls console.print."""
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
        print_records_with_summary(
            records,
            summary=None,
            start_dt=1640995200,
            end_dt=1640996000,
        )
        mock_console.print.assert_called_once()


def test_print_records_with_summary_with_show_index():
    """Test print_records_with_summary with show_index parameter."""
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
        print_records_with_summary(
            records,
            summary=False,
            start_dt=1640995200,
            end_dt=1640996000,
            show_index=True,
        )
        mock_console.print.assert_called_once()


def test_print_records_with_summary_with_show_keys():
    """Test print_records_with_summary with show_keys parameter."""
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
        print_records_with_summary(
            records,
            summary=False,
            start_dt=1640995200,
            end_dt=1640996000,
            show_keys=True,
        )
        mock_console.print.assert_called_once()


def test_print_records_with_summary_with_record_status():
    """Test print_records_with_summary with record_status parameter."""
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
        print_records_with_summary(
            records,
            summary=False,
            start_dt=1640995200,
            end_dt=1640996000,
            record_status={"abc123": "modified"},
        )
        mock_console.print.assert_called_once()
