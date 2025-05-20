import os
import subprocess
import sys
from datetime import datetime
from time import time

import click

from .rich_utils import console
from .types import Record


def open_file(path: str, editor: str | None = None) -> None:
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
        console.print(f"Edit the file at: {path}")


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


def readable_time(timestamp) -> str:
    """
    Turn a timestamp into a readable string.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        A string representing the timestamp in 'YYYY-MM-DD HH:MM' format.
    """
    value = datetime.fromtimestamp(timestamp)
    return f"{value:%Y-%m-%d %H:%M}"


def readable_duration(nsecs) -> str:
    """
    Turn a duration in seconds into a reabable string.

    Args:
        nsecs: The duration in seconds.

    Returns:
        A string representing the duration in 'HH:MM' format.
    """
    m = round(nsecs / 60)
    return f"{m // 60:02.0f}:{m % 60:02.0f}"


def print_records(records: list[Record]) -> None:
    """
    Pretty-print a list of records.

    Args:
        records: A list of records.
    """
    # Sort
    records = sorted(records, key=lambda r: r["t1"])

    # Write header
    print(f"{'Started':>17} {'Stopped':>17} {'Duration':>9}  Description")

    # Write each record
    for r in records:
        started = readable_time(r["t1"])
        if r["t1"] == r["t2"]:
            stopped = "-"
            duration = readable_duration(time() - r["t1"])
        else:
            stopped = readable_time(r["t2"])
            duration = readable_duration(r["t2"] - r["t1"])
            if stopped.split(" ")[0] == started.split(" ")[0]:
                stopped = stopped.split(" ", 1)[1]
        description = " " + r.get("ds", "")
        click.echo(f"{started:>17} {stopped:>17} {duration:>9} {description}")


def print_records_csv(records: list[Record]) -> None:
    """
    Print records in CSV format.

    Args:
        records: A list of records.
    """
    # Sort
    records = sorted(records, key=lambda r: r["t1"])

    # Write header
    print("Started,Stopped,Duration,Description")

    # Write each record
    for r in records:
        started = readable_time(r["t1"])
        if r["t1"] == r["t2"]:
            stopped = ""
            duration = readable_duration(time() - r["t1"])

        else:
            stopped = readable_time(r["t2"])
            duration = readable_duration(r["t2"] - r["t1"])
            if stopped.split(" ")[0] == started.split(" ")[0]:
                stopped = stopped.split(" ", 1)[1]
        description = " " + r.get("ds", "")
        click.echo(f"{started},{stopped},{duration},{description}")
