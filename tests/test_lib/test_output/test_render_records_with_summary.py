"""Tests for the render_records_with_summary function."""

from io import StringIO

from rich.console import Console, Group

from better_timetagger_cli.lib.output import render_records_with_summary
from better_timetagger_cli.lib.types import Record


def render_to_string(group: Group) -> str:
    """Helper to render a rich group to string."""
    string_io = StringIO()
    console = Console(file=string_io, legacy_windows=False)
    console.print(group)
    return string_io.getvalue()


def test_render_records_with_summary_returns_group():
    """Return a Group object."""
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

    result = render_records_with_summary(
        records,
        summary=None,
        start_dt=1640995200,
        end_dt=1640996000,
    )

    assert isinstance(result, Group)


def test_render_records_with_summary_both():
    """Display both summary and records when summary=None."""
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

    result = render_records_with_summary(
        records,
        summary=None,
        start_dt=1640995200,
        end_dt=1640996000,
    )
    output = render_to_string(result)

    assert "Total:" in output  # From summary
    assert "#work" in output  # From records


def test_render_records_with_summary_only_summary():
    """Display only summary when summary=True."""
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

    result = render_records_with_summary(
        records,
        summary=True,
        start_dt=1640995200,
        end_dt=1640996000,
    )
    output = render_to_string(result)

    assert "Total:" in output
    assert "10m" in output


def test_render_records_with_summary_only_records():
    """Display only records when summary=False."""
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

    result = render_records_with_summary(
        records,
        summary=False,
        start_dt=1640995200,
        end_dt=1640996000,
    )
    output = render_to_string(result)

    assert "#work" in output


def test_render_records_with_summary_passes_show_index():
    """Pass through show_index option to render_records."""
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

    result = render_records_with_summary(
        records,
        summary=False,
        start_dt=1640995200,
        end_dt=1640996000,
        show_index=True,
    )
    output = render_to_string(result)

    assert "[0]" in output


def test_render_records_with_summary_passes_show_keys():
    """Pass through show_keys option to render_records."""
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

    result = render_records_with_summary(
        records,
        summary=False,
        start_dt=1640995200,
        end_dt=1640996000,
        show_keys=True,
    )
    output = render_to_string(result)

    assert "abc123" in output


def test_render_records_with_summary_passes_record_status():
    """Pass through record_status option to render_records."""
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

    result = render_records_with_summary(
        records,
        summary=False,
        start_dt=1640995200,
        end_dt=1640996000,
        record_status={"abc123": "modified"},
    )
    output = render_to_string(result)

    assert "modified" in output
