"""
# Utilities based on `rich` to render formatted output.
"""

from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Any

from rich.box import SIMPLE
from rich.table import Table
from rich.text import Text

from .api import Record
from .config import load_config
from .console import console
from .misc import now_timestamp


def print_records(
    records: Iterable[Record] = (),
    *,
    started: Iterable[Record] = (),
    running: Iterable[Record] = (),
    stopped: Iterable[Record] = (),
    show_keys: bool = False,
) -> None:
    """
    Display records in a table format using rich.

    Apply different styles based on the record status (started, running, stopped).

    Args:
        records: A list of records to display.
        started: A list of records that are started.
        running: A list of records that are running.
        stopped: A list of records that are stopped.
        show_keys: If True, show the key of each record.
    """
    output = render_records(
        records,
        started=started,
        running=running,
        stopped=stopped,
        show_keys=show_keys,
    )
    console.print(output)


def render_records(
    records: Iterable[Record] = (),
    *,
    started: Iterable[Record] = (),
    running: Iterable[Record] = (),
    stopped: Iterable[Record] = (),
    show_keys: bool = False,
) -> Table:
    """
    Create a renderable rich object to display records.

    Apply different styles based on the record status (started, running, stopped).

    Args:
        records: A list of records to display.
        started: A list of records that are started.
        running: A list of records that are running.
        stopped: A list of records that are stopped.
        show_key: If True, show the key of each record.
    """
    now = now_timestamp()

    table = Table(box=SIMPLE, min_width=65)
    if show_keys:
        table.add_column("Key", style="blue", no_wrap=True)
    table.add_column(style="cyan", no_wrap=True)
    table.add_column("Started", style="cyan")
    table.add_column("Stopped", style="cyan")
    table.add_column("Duration", style="bold magenta", no_wrap=True)
    table.add_column("Description", style="green")

    def _add_row(key: str, *args, **kwargs) -> None:
        """Optionally include the 'key' column."""
        if show_keys:
            args = tuple(key, *args)
        table.add_row(*args, **kwargs)

    for r in records:
        _add_row(
            r["key"],
            readable_weekday(r["t1"]),
            readable_date_time(r["t1"]),
            readable_date_time(r["t2"]) if r["t1"] != r["t2"] else "...",
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
        )

    for r in started:
        _add_row(
            r["key"],
            readable_weekday(r["t1"]),
            readable_date_time(now),
            "...",
            "...",
            highlight_tags_in_description(r["ds"]),
            style="green",
        )

    for r in running:
        _add_row(
            r["key"],
            readable_weekday(r["t1"]),
            readable_date_time(r["t1"]),
            "...",
            readable_duration(now - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="cyan",
        )

    for r in stopped:
        _add_row(
            r["key"],
            readable_weekday(r["t1"]),
            readable_date_time(r["t1"]),
            readable_date_time(r["t2"]),
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="red",
        )

    return table


def readable_date_time(timestamp: int | float | datetime) -> str:
    """
    Turn a timestamp into a readable string.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        A string representing the timestamp in date and time format.
    """
    config = load_config()

    if isinstance(timestamp, datetime):
        value = timestamp
    else:
        value = datetime.fromtimestamp(timestamp)

    return value.strftime(config["datetime_format"])


def readable_weekday(timestamp: int | float | datetime) -> str:
    """
    Turn a timestamp into a readable string.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        A string representing the timestamp as weekday
    """
    config = load_config()

    if isinstance(timestamp, datetime):
        value = timestamp
    else:
        value = datetime.fromtimestamp(timestamp)

    return value.strftime(config["weekday_format"])


def readable_duration(duration: int | float | timedelta) -> str:
    """
    Turn a duration in seconds into a reabable string.

    Args:
        nsecs: The duration in seconds.

    Returns:
        A string representing the duration in 'HH:MM' format.
    """
    if isinstance(duration, timedelta):
        total_seconds = duration.total_seconds()
    else:
        total_seconds = duration

    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours:.0f}h")

    parts.append(f"{minutes:.0f}m")

    return " ".join(parts)


def styled_padded(value: Any, width: int = 5, *, style: str = "magenta", padding_style: str = "dim magenta", padding: str = "0") -> Text:
    value_str = str(value)
    len_padding = width - len(value_str)

    if len_padding <= 0:
        return Text(value_str, style=style)
    else:
        text = Text()
        text.append(padding * len_padding, style=padding_style)
        text.append(value_str, style=style)
        return text


def highlight_tags_in_description(description: str, style: str = "underline") -> Text:
    """
    Highlight tags (marked by '#') in record descriptions.

    Args:
        description: The description string.

    Returns:
        A Text object with highlighted tags.
    """
    text = Text()
    for word in description.split():
        if word.startswith("#"):
            text.append(" ")
            text.append(word, style=style)
        else:
            text.append(f" {word}")
    return text
