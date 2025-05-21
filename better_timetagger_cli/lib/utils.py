import os
import secrets
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime
from time import time
from typing import Any

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


def highlight_tags_in_description(description: str) -> Text:
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
            text.append(word, style="bold underline")
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

    table = Table(box=SIMPLE, expand=True)
    table.add_column("Started", justify="right", style="cyan", no_wrap=True)
    table.add_column("Stopped", justify="left", style="cyan", no_wrap=True)
    table.add_column("Duration", justify="left", style="green", no_wrap=True)
    table.add_column("Description", justify="left", style="magenta", no_wrap=True)

    for r in records:
        table.add_row(
            readable_time(r["t1"]),
            readable_time(r["t2"]) if r["t1"] != r["t2"] else "...",
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
        )

    for r in started:
        table.add_row(
            readable_time(now),
            "...",
            "...",
            highlight_tags_in_description(r["ds"]),
            style="green",
        )

    for r in running:
        table.add_row(
            readable_time(r["t1"]),
            "...",
            readable_duration(now - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="cyan",
        )

    for r in stopped:
        table.add_row(
            readable_time(r["t1"]),
            readable_time(r["t2"]),
            readable_duration(r["t2"] - r["t1"]),
            highlight_tags_in_description(r["ds"]),
            style="dim red",
        )

    print(table)


def edit_file(path: str, editor: str | None = None) -> None:
    """
    Open a file in the system's default editor or a specified editor.

    Args:
        path: The path to the file to open.
        editor: The name or path of the editor executable. Default to system default.
    """
    try:
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

        else:
            raise NotImplementedError(f"Platform {sys.platform} not supported")

    except Exception:
        print(f"Edit the file at: {path}")


def user_config_dir(appname=None, roaming=False) -> str:
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


def readable_time(timestamp: int | float) -> str:
    """
    Turn a timestamp into a readable string.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        A string representing the timestamp in 'YYYY-MM-DD HH:MM' format.
    """
    value = datetime.fromtimestamp(timestamp)
    return f"{value:%Y-%m-%d %H:%M}"


def readable_duration(duration: int | float) -> str:
    """
    Turn a duration in seconds into a reabable string.

    Args:
        nsecs: The duration in seconds.

    Returns:
        A string representing the duration in 'HH:MM' format.
    """
    m = round(duration / 60)
    return f"{m // 60:02.0f}:{m % 60:02.0f}"


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
