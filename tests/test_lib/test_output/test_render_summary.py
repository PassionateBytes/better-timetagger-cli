"""Tests for the render_summary function."""

from datetime import datetime
from io import StringIO

from rich.console import Console
from rich.table import Table

from better_timetagger_cli.lib.output import render_summary
from better_timetagger_cli.lib.types import Record


def render_to_string(table: Table) -> str:
    """Helper to render a rich table to string."""
    string_io = StringIO()
    console = Console(file=string_io, legacy_windows=False)
    console.print(table)
    return string_io.getvalue()


def test_render_summary_returns_table():
    """Return a Table object."""
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

    result = render_summary(records, start_dt=1640995200, end_dt=1640996000)

    assert isinstance(result, Table)


def test_render_summary_with_single_record():
    """Display summary for single record."""
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

    result = render_summary(records, start_dt=1640995200, end_dt=1640996000)
    output = render_to_string(result)

    assert "Total:" in output
    assert "1" in output  # record count
    assert "10m" in output  # duration


def test_render_summary_with_multiple_records():
    """Display summary for multiple records."""
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
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996400,
            "ds": "#meeting",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
    ]

    result = render_summary(records, start_dt=1640995200, end_dt=1640996500)
    output = render_to_string(result)

    assert "Total:" in output
    assert "2" in output  # record count
    assert "20m" in output  # total duration


def test_render_summary_with_tags():
    """Display tag statistics in summary."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995800,
            "ds": "#work #project",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 600,
        },
        {
            "key": "def456",
            "mt": 1640995200,
            "t1": 1640995800,
            "t2": 1640996100,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": False,
            "_duration": 300,
        },
    ]

    result = render_summary(records, start_dt=1640995200, end_dt=1640996200)
    output = render_to_string(result)

    assert "#work:" in output
    assert "#project:" in output


def test_render_summary_with_datetime_objects():
    """Accept datetime objects for start and end."""
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

    start = datetime.fromtimestamp(1640995200)
    end = datetime.fromtimestamp(1640996000)

    result = render_summary(records, start_dt=start, end_dt=end)
    output = render_to_string(result)

    assert "Total:" in output
    assert "10m" in output


def test_render_summary_with_empty_records():
    """Handle empty record list."""
    records: list[Record] = []

    result = render_summary(records, start_dt=1640995200, end_dt=1640996000)
    output = render_to_string(result)

    assert "Total:" in output
    assert "0" in output  # zero records
