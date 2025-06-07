"""
# Utilities based on `rich` to render formatted output.
"""

import re
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
    *records: tuple[Iterable[Record] | Record, str] | Iterable[Record] | Record,
    show_index: bool = False,
    show_keys: bool = False,
    record_status: dict[str, str | None] | None = None,
) -> None:
    """
    Display records in a table format using rich.

    Args:
        records: One or more lists of records to display. Optionally, provide along with a style expression as a tuple.
        show_index: If True, show the row index of each record. Useful for row-select prompts.
        show_keys: If True, show the key (unique identifier) of each record.
        record_status: A map of status annotations for each record key.
    """
    output = render_records(
        *records,
        show_index=show_index,
        show_keys=show_keys,
        record_status=record_status,
    )
    console.print(output)


def render_records(
    *records: tuple[Iterable[Record] | Record, str] | Iterable[Record] | Record,
    show_keys: bool = False,
    show_index: bool = False,
    record_status: dict[str, str | None] | None = None,
) -> Table:
    """
    Create a renderable rich object to display records.

    Args:
        records: One or more lists of records to display. Optionally, provide along with a style expression as a tuple.
        show_index: If True, show the row index of each record. Useful for row-select prompts.
        show_keys: If True, show the key (unique identifier) of each record.
        record_status: A map of status annotations for each record key.
    """
    now = now_timestamp()

    table = Table(box=SIMPLE, min_width=65)

    # extra columns left
    if show_index:
        table.add_column(style="blue", no_wrap=True)
    if show_keys:
        table.add_column("Key", style="blue", no_wrap=True)

    # main columns
    table.add_column(style="cyan", no_wrap=True)
    table.add_column("Started", style="cyan")
    table.add_column("Stopped", style="cyan")
    table.add_column("Duration", style="bold magenta", no_wrap=True, justify="right")
    table.add_column("Description", style="green")

    # extra columns right
    if record_status:
        table.add_column("Status", style="yellow")

    # unpack records and associated styles
    for records_input in records:
        if isinstance(records_input, tuple) and isinstance(records_input[0], list | dict) and isinstance(records_input[1], str):
            _records, _style = records_input
        else:
            _records, _style = records_input, None
        if isinstance(_records, dict):
            _records = (_records,)

        # render records into table rows
        for i, r in enumerate(_records):
            columns: tuple[str, ...] = (
                readable_weekday(r["t1"]),
                readable_date_time(r["t1"]),
                readable_date_time(r["t2"]) if r["t1"] != r["t2"] else "...",
                readable_duration(r["t2"] - r["t1"]) if r["t1"] != r["t2"] else readable_duration(now - r["t1"]),
                highlight_tags_in_description(r["ds"]),
            )
            # extra columns left
            if show_keys:
                columns = (r["key"], *columns)
            if show_index:
                columns = (f"[blue]\[{i}][/blue]" if i <= 0 else f"[dim]\[{i}][/dim]", *columns)
            # extra columns right
            if record_status:
                columns = (*columns, f"[yellow]{record_status.get(r['key'], '')}[/yellow]")

            table.add_row(*columns, style=_style)

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

    output = ""
    if hours:
        output += f"{hours}h "
    output += f"{minutes:>2}m"

    return output.strip()


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


def highlight_tags_in_description(description: str, style: str = "underline") -> str:
    """
    Highlight tags (marked by '#') in record descriptions.

    Args:
        description: The description string.

    Returns:
        A Text object with highlighted tags.
    """
    return re.sub(r"#\S+", lambda m: f"[{style}]{m.group(0)}[/{style}]", description.replace("\\", ""))
