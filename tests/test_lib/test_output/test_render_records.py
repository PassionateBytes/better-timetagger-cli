"""Tests for the render_records function."""

from io import StringIO

from rich.console import Console
from rich.table import Table

from better_timetagger_cli.lib.output import render_records
from better_timetagger_cli.lib.types import Record


def render_to_string(table: Table) -> str:
    """Helper to render a rich table to string."""
    string_io = StringIO()
    console = Console(file=string_io, legacy_windows=False)
    console.print(table)
    return string_io.getvalue()


def test_render_records_returns_table():
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

    result = render_records(records)

    assert isinstance(result, Table)


def test_render_records_with_single_record():
    """Display single record in table."""
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

    result = render_records(records)
    output = render_to_string(result)

    assert "#work" in output
    assert "10m" in output


def test_render_records_with_multiple_records():
    """Display multiple records in table."""
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

    result = render_records(records)
    output = render_to_string(result)

    assert "#work" in output
    assert "#meeting" in output


def test_render_records_with_show_index():
    """Display row index when show_index is True."""
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

    result = render_records(records, show_index=True)
    output = render_to_string(result)

    assert "[0]" in output


def test_render_records_with_show_keys():
    """Display record keys when show_keys is True."""
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

    result = render_records(records, show_keys=True)
    output = render_to_string(result)

    assert "abc123" in output


def test_render_records_with_running_record():
    """Display '...' for running records."""
    records: list[Record] = [
        {
            "key": "abc123",
            "mt": 1640995200,
            "t1": 1640995200,
            "t2": 1640995200,
            "ds": "#work",
            "st": 1640995200.0,
            "_running": True,
            "_duration": 0,
        }
    ]

    result = render_records(records)
    output = render_to_string(result)

    assert "..." in output


def test_render_records_with_record_status():
    """Display status column when record_status provided."""
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

    result = render_records(records, record_status={"abc123": "modified"})
    output = render_to_string(result)

    assert "modified" in output


def test_render_records_with_styled_records():
    """Accept records with style specification as tuple."""
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

    result = render_records((records, "dim"))
    output = render_to_string(result)

    assert "#work" in output


def test_render_records_with_single_dict():
    """Accept a single record as a dict instead of a list."""
    record: Record = {
        "key": "abc123",
        "mt": 1640995200,
        "t1": 1640995200,
        "t2": 1640995800,
        "ds": "#work",
        "st": 1640995200.0,
        "_running": False,
        "_duration": 600,
    }

    result = render_records(record)
    output = render_to_string(result)

    assert "#work" in output
    assert "10m" in output
