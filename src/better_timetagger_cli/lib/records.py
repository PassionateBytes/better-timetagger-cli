"""
### Record Processing & Analysis

Functions to manipulate, analyse and process time tracking records.
"""

import re
import secrets
from collections.abc import Iterable
from datetime import datetime
from typing import Literal, TypeVar

from .timestamps import now_timestamp, round_timestamp
from .types import Record, Settings


def create_record_key(length: int = 8) -> str:
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
    return "".join([secrets.choice(chars) for _ in range(length)])


def post_process_records(
    records: list[Record],
    *,
    tags: list[str] | None = None,
    tags_match: Literal["any", "all"] = "any",
    sort_desc: bool = False,
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
        sort_desc: Whether to sort in reverse order. Defaults to True.
        hidden: Whether to show hidden (i.e. deleted) records. Defaults to False.
        running: Whether to list only running records (where t1 == t2). Defaults to False.

    Returns:
        A list of post-processed records.
    """
    now = now_timestamp()

    records = [
        {
            "key": r.get("key", ""),
            "mt": r.get("mt", 0),
            "t1": r.get("t1", 0),
            "t2": r.get("t2", 0),
            "ds": r.get("ds", ""),
            "st": r.get("st", 0),
            "_running": r.get("t1", 0) == r.get("t2", 0),  # determine running state
            "_duration": (r.get("t2", 0) if r.get("t1", 0) != r.get("t2", 0) else now) - r.get("t1", 0),  # determine duration
        }
        for r in records
        if check_record_tags_match(r, tags, tags_match)  # filter by tags
        and r["ds"].startswith("HIDDEN") == hidden  # filter by hidden status
        and (not running or r["t1"] == r["t2"])  # filter by running status
    ]
    records.sort(key=lambda r: r["t2" if sort_desc else "t1"], reverse=sort_desc)
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
    rounded_records = []

    for record in records:
        duration_rounded = round_timestamp(record["_duration"], round_to)
        t1_rounded = round_timestamp(record["t1"], round_to)
        t2_rounded = t1_rounded + duration_rounded

        rounded_records.append(
            Record(
                {
                    **record,
                    "t1": t1_rounded,
                    "t2": t2_rounded,
                    "_duration": duration_rounded,
                }
            )
        )

    return rounded_records


def get_total_time(records: Iterable[Record], start: int | datetime, end: int | datetime) -> int:
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


def get_tag_stats(records: Iterable[Record]) -> dict[str, tuple[int, int]]:
    """
    Get statistics for each tag in the records. Results are sorted by tag's total duration.

    Args:
        records: A list of records.

    Returns:
        A tuple with 1) the number of occurrences of the tag and 2) the total duration for that tag.
    """
    now = now_timestamp()
    tag_stats: dict[str, tuple[int, int]] = {}

    for r in records:
        for tag in get_tags_from_description(r["ds"]):
            stats = tag_stats.get(tag, (0, 0))
            t1 = r["t1"]
            t2 = r["t2"] if not r["_running"] else now
            duration = t2 - t1
            tag_stats[tag] = (
                stats[0] + 1,
                stats[1] + duration,
            )

    tag_stats = dict(sorted(tag_stats.items(), key=lambda x: x[1][1], reverse=True))

    return tag_stats
