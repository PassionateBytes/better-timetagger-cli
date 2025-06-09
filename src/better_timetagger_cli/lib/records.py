"""
# Utilities for handling TimeTagger records.
"""

import re
import sys
from collections.abc import Generator, Iterable
from datetime import datetime, timezone
from typing import Literal, TypeVar

from .misc import abort, now_timestamp
from .types import Record, Settings


def get_total_time(records: list[Record], start: int | datetime, end: int | datetime) -> int:
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
    now = now_timestamp()

    if isinstance(start, datetime):
        start = int(start.timestamp())
    if isinstance(end, datetime):
        end = int(end.timestamp())

    for r in records:
        t1 = r["t1"]
        t2 = r["t2"] if not r["_running"] else now
        total += min(end, t2) - max(start, t1)

    return total


def get_record_duration(record: Record) -> int:
    """
    Get the duration of a record.

    Args:
        record: A record dictionary containing 't1' and 't2' timestamps.

    Returns:
        The duration in seconds.
    """
    now = now_timestamp()
    t1 = record["t1"]
    t2 = record["t2"] if not record["_running"] else now
    return t2 - t1


def get_tag_stats(records: list[Record]) -> dict[str, tuple[int, int]]:
    """
    Get statistics for each tag in the records. Results are sorted by tag's total duration.

    Args:
        records: A list of records.

    Returns:
        A tuple with 1) the number of occurrences of the tag and 2) the total duration for that tag.
    """

    tag_stats: dict[str, tuple[int, int]] = {}
    for r in records:
        for tag in get_tags_from_description(r["ds"]):
            stats = tag_stats.get(tag, (0, 0))
            tag_stats[tag] = (
                stats[0] + 1,
                stats[1] + get_record_duration(r),
            )

    tag_stats = dict(sorted(tag_stats.items(), key=lambda x: x[1][1], reverse=True))

    return tag_stats


def post_process_records(
    records: list[Record],
    *,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_by: Literal["t1", "t2", "st", "mt", "ds"] = "t2",
    sort_reverse: bool = True,
    hidden: bool = False,
    running: bool = False,
) -> list[Record]:
    """
    Post-process records after fetching them from the API.

    This includes sorting, filtering by tags, and manage hidden records.

    Args:
        records: A list of records to post-process.
        tags: A list of tags to filter records by. Defaults to None.
        tags_match: The mode to match tags. Can be "any" or "all". Defaults to "any".
        sort_by: The field to sort the records by. Can be "t1", "t2", "st", "mt", or "ds". Defaults to "t2".
        sort_reverse: Whether to sort in reverse order. Defaults to True.
        hidden: Whether to show hidden (i.e. deleted) records. Defaults to False.
        running: Whether to list only running records (where t1 == t2). Defaults to False.

    Returns:
        A list of post-processed records.
    """
    records = [
        {
            "key": r.get("key", ""),
            "mt": r.get("mt", 0),
            "t1": r.get("t1", 0),
            "t2": r.get("t2", 0),
            "ds": r.get("ds", ""),
            "st": r.get("st", 0),
            "_running": r["t1"] == r["t2"],  # determine running state
        }
        for r in records
        if check_record_tags_match(r, tags, tags_match)  # filter by tags
        and r["ds"].startswith("HIDDEN") == hidden  # filter by hidden status
        and (not running or r["t1"] == r["t2"])  # filter by running status
    ]
    records.sort(key=lambda r: r[sort_by], reverse=sort_reverse)
    return records


def check_record_tags_match(
    record: Record,
    tags: list[str] | None,
    tags_match: Literal["any", "all"],
) -> bool:
    """
    Check if the record matches the provided tags.

    Args:
        record: The record to check.
        tags: The tags to match against.
        tags_match: The matching mode ('any' or 'all').

    Returns:
        True if the record matches the tags, False otherwise.
    """
    if not tags:
        return True
    match_func = any if tags_match == "any" else all
    return match_func(tag in record["ds"] for tag in tags)


_T = TypeVar("_T", bound=Record | Settings)


def merge_by_key(
    updated_data: list[_T],
    original_data: list[_T],
) -> list[_T]:
    """
    Merge two lists of records or settings by their keys.

    Args:
        updated_data: The updated data to merge.
        original_data: The original data to merge with.

    Returns:
        A list of merged records or settings.
    """
    updates_key_map = {obj["key"]: obj for obj in updated_data}
    merged_data = []
    while original_data:
        obj = original_data.pop(0)
        updated_obj = updates_key_map.pop(obj["key"], obj)
        merged_data.append(updated_obj)
    merged_data.extend(updates_key_map.values())
    return merged_data


def records_to_csv(records: Iterable[Record]) -> str:
    """
    Convert records to CSV.

    This produces the same CSV format as the TimeTagger web app.

    Args:
        records: A list of records to convert.

    Returns:
        A string representing the records in CSV format.
    """
    header = ("key", "start", "stop", "tags", "description")
    newline = "\n" if not sys.platform.startswith("win") else "\r\n"
    separator = "\t"

    lines = [
        (
            r.get("key", ""),
            datetime.fromtimestamp(r.get("t1", 0), tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            datetime.fromtimestamp(r.get("t2", 0), tz=timezone.utc).isoformat().replace("+00:00", "Z") if not r["_running"] else "",
            " ".join(get_tags_from_description(r.get("ds", ""))),
            r.get("ds", ""),
        )
        for r in records
    ]
    lines = [header, *lines]

    # - substitute unsafe whitespace
    # - join fields with separator
    # - join lines with newline
    return newline.join(separator.join(re.sub(r"\s+", " ", str(field)) for field in line) for line in lines)


def get_tags_from_description(description: str) -> list[str]:
    """
    Extract tags from a description string.

    Args:
        description: The description string.

    Returns:
        A list of tags extracted from the description.
    """
    return re.findall(r"#\S+", description)


def round_records(records: list[Record], round_to: int) -> list[Record]:
    """
    Round start and end times of records to the nearest specified minute-interval.

    Instead of simply rounding both the start and end times to their nearest interval,
    we round based on the duration of the record. This ensures the resulting record
    duration remains consistent and accurate.

    Args:
        records: A list of records to round.
        round_to: The number of minutes to round to (e.g., 5 for 5-minute intervals).

    Returns:
        A list of records with rounded start and end times.
    """
    round_to_seconds = round_to * 60
    rounded_records = []

    for record in records:
        duration_rounded = round((record["t2"] - record["t1"]) / round_to_seconds) * round_to_seconds
        t1_rounded = round(record["t1"] / round_to_seconds) * round_to_seconds
        t2_rounded = t1_rounded + duration_rounded

        rounded_records.append(
            Record(
                {
                    **record,
                    "t1": t1_rounded,
                    "t2": t2_rounded,
                }
            )
        )

    return rounded_records


def records_from_csv(
    file: Generator[str],
) -> list[Record]:
    """
    Load records from a CSV file.

    Args:
        file: An iterable of lines from a CSV file.

    Returns:
        A list of records loaded from the CSV file.
    """
    header = ("key", "start", "stop", "tags", "description")
    now = now_timestamp()
    records = []

    header_line = next(file)
    for separator in ("\t", ",", ";"):
        header_fields = header_line.strip().split(separator)
        if all(required in header_fields for required in header):
            break
    else:
        abort(
            f"Failed to import CSV: Missing fields in header.\n"
            f"[dim]First line must contain each of: {', '.join(header)}"
            f"\nLine 1: \\[{header_line.strip()}][/dim]"
        )

    header_map = {field: header_fields.index(field) for field in header}

    for i, line in enumerate(file, start=2):
        fields = line.strip("\r\n").split(separator)
        if len(fields) != len(header_fields):
            abort(
                f"Failed to import CSV: Inconsistent number of columns.\n"
                f"[dim]Header has {len(header_fields)} columns, line {i} has {len(fields)} columns.\n"
                f"Line {i}: \\[{line.strip()}][/dim]"
            )

        try:
            t1_import = fields[header_map["start"]].strip().replace("Z", "+00:00")
            t2_import = fields[header_map["stop"]].strip().replace("Z", "+00:00") or t1_import
            t1 = int(datetime.fromisoformat(t1_import).timestamp())
            t2 = int(datetime.fromisoformat(t2_import).timestamp())
            record: Record = {
                "key": fields[header_map["key"]].strip(),
                "t1": t1,
                "t2": t2,
                "ds": fields[header_map["description"]].strip(),
                "mt": now,
                "st": 0,
                "_running": t1 == t2,  # determine running state
            }
        except Exception as e:
            abort(f"Failed to import CSV: {e.__class__.__name__}\n[dim]{e}\nLine {i}: \\[{line.strip()}][/dim]")

        records.append(record)

    return records
