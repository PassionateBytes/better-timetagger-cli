import os
import secrets
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime, timedelta
from time import time
from typing import Any, NoReturn

import click
from rich import print
from rich.box import SIMPLE
from rich.table import Table
from rich.text import Text

from .types import Record


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


def print_records(
    records: list[Record] = (),
    *,
    started: Iterable[Record] = (),
    running: Iterable[Record] = (),
    stopped: Iterable[Record] = (),
) -> None:
    """
    Print records in a table format.

    Apply different styles based on the record status (started, running, stopped).
    """
    now = int(time())

    table = Table(box=SIMPLE, min_width=65)
    table.add_column("Started", style="cyan", no_wrap=True)
    table.add_column("Stopped", style="cyan", no_wrap=True)
    table.add_column("Duration", style="bold magenta", no_wrap=True)
    table.add_column("Description", style="green", no_wrap=True)

    for r in records:
        table.add_row(
            readable_date_time(r["t1"]),
            readable_date_time(r["t2"]) if r["t1"] != r["t2"] else "...",
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
        )

    for r in started:
        table.add_row(
            readable_date_time(now),
            "...",
            "...",
            highlight_tags_in_description(r["ds"]),
            style="green",
        )

    for r in running:
        table.add_row(
            readable_date_time(r["t1"]),
            "...",
            readable_duration(now - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="cyan",
        )

    for r in stopped:
        table.add_row(
            readable_date_time(r["t1"]),
            readable_date_time(r["t2"]),
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="red",
        )

    print(table)


def get_record_duration(record: Record) -> int:
    """
    Get the duration of a record.

    Args:
        record: A record dictionary containing 't1' and 't2' timestamps.

    Returns:
        The duration in seconds.
    """
    now = int(time())
    t1 = record["t1"]
    t2 = record["t2"] if record["t1"] != record["t2"] else now
    return t2 - t1


def get_tag_stats(records: list[Record]) -> dict[str, tuple[int, int]]:
    """
    Get statistics for each tag in the records. Results are sorted by tag's total duration.

    Args:
        records: A list of records.

    Returns:
        A tuple with 1) the number of occurrences of the tag and 2) the total duration for that tag.
    """

    tag_stats = {}
    for r in records:
        for word in r["ds"].split():
            if word.startswith("#"):
                stats = tag_stats.get(word, (0, 0))
                tag_stats[word] = (
                    stats[0] + 1,
                    stats[1] + get_record_duration(r),
                )

    tag_stats = dict(sorted(tag_stats.items(), key=lambda x: x[1][1], reverse=True))

    return tag_stats


def edit_file(path: str, editor: str | None = None) -> None:
    """
    Open a file in the system's default editor or a specified editor.

    Args:
        path: The path to the file to open.
        editor: The name or path of the editor executable. Default to system default.
    """
    if editor:
        subprocess.call((editor, path))
        return

    if sys.platform.startswith("darwin"):
        subprocess.call(("open", path))

    elif sys.platform.startswith("win"):
        if " " in path:
            # see: http://stackoverflow.com/a/72796/2271927
            subprocess.call(("start", "", path), shell=True)
        else:
            subprocess.call(("start", path), shell=True)

    elif sys.platform.startswith("linux"):
        try:
            # see: http://superuser.com/questions/38984/linux-equivalent-command-for-open-command-on-mac-windows
            subprocess.call(("xdg-open", path))
        except FileNotFoundError:
            subprocess.call((os.getenv("EDITOR", "vi"), path))


def get_config_dir(appname=None, roaming=False) -> str:
    """
    Get the directory to store app config files.

    Args:
        appname: The name of the application subdirectory.
        roaming: If True, use roaming profile on Windows.

    Returns:
        The path to the config directory.
    """
    if sys.platform.startswith("darwin"):
        path = os.path.expanduser("~/Library/Preferences/")

    elif sys.platform.startswith("win"):
        path1, path2 = os.getenv("LOCALAPPDATA"), os.getenv("APPDATA")
        path = (path2 or path1) if roaming else (path1 or path2)
        path = os.path.normpath(path)

    else:
        path = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    if not (path and os.path.isdir(path)):
        path = os.path.expanduser("~")

    if appname:
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    return str(path)


def total_time(records: list[Record], start: datetime, end: datetime) -> int:
    """
    Calculate the total time spent on records within a given time range.

    Args:
        records: A list of records, each containing 't1' and 't2' timestamps.
        start: The start datetime of the time range.
        end: The end datetime of the time range.

    Returns:
        The total time in seconds spent on the records within the time range.
    """
    total = 0
    t_start = start.timestamp()
    t_end = end.timestamp()
    t_now = datetime.now().timestamp()
    for r in records:
        t1 = r["t1"]
        t2 = r["t2"] if r["t1"] != r["t2"] else t_now
        total += min(t_end, t2) - max(t_start, t1)
    return total


def readable_date_time(timestamp: int | float | datetime) -> str:
    """
    Turn a timestamp into a readable string.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        A string representing the timestamp in 'YYYY-MM-DD HH:MM' format.
    """
    if isinstance(timestamp, datetime):
        value = timestamp
    else:
        value = datetime.fromtimestamp(timestamp)
    return f"{value:%Y-%m-%d %H:%M}"


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


def generate_uid(length: int = 8) -> str:
    """
    Generate a unique id for records, in the form of an 8-character string.

    The value is used to uniquely identify the record of one user.
    Assuming a user who has been creating 100 records a day, for 20 years (about 1M records),
    the chance of a collision for a new record is about 1 in 50 milion.

    Args:
        length: The length of the random string to generate. Default is 8.

    Returns:
        A string of 8 random characters.
    """
    chars = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([secrets.choice(chars) for i in range(length)])


def unify_tags_callback(ctx: click.Context, param: click.Parameter, tags: list[str]) -> list[str]:
    """
    Click option callback to unify tags.

    Ensure tags start with '#' and remove duplicates.

    Args:
        tags: A list of tags.

    Returns:
        A list of unique tags.
    """
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]
    tags = list(set(tags))
    return tags


def abort(message: str) -> NoReturn:
    """
    Abort the current command with a message.

    Args:
        message: The message to display before aborting.
    """
    print(f"\n[red]{message}[/red]\n")
    exit(1)
