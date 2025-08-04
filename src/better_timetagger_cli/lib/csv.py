"""
### CSV Import/Export

Functions to load or save records in CSV format.
"""

import re
import sys
from collections.abc import Generator, Iterable
from datetime import datetime, timezone

from .console import abort
from .timestamps import now_timestamp
from .records import get_tags_from_description
from .types import Record


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


def records_from_csv(
    file: Generator[str],
    *,
    start: int | datetime | None = None,
    end: int | datetime | None = None,
) -> list[Record]:
    """
    Load records from a CSV file.

    Args:
        file: An iterable of lines from a CSV file.
        start: The start time to filter records. Can be a timestamp or a datetime object.
        end: The end time to filter records. Can be a timestamp or a datetime object.

    Returns:
        A list of records loaded from the CSV file.
    """
    if isinstance(start, datetime):
        start = int(start.timestamp())
    if isinstance(end, datetime):
        end = int(end.timestamp())

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
                "_duration": (t2 if t1 != t2 else now) - t1,  # determine duration
            }
        except Exception as e:
            abort(f"Failed to import CSV: {e.__class__.__name__}\n[dim]{e}\nLine {i}: \\[{line.strip()}][/dim]")

        # filter by date/time range
        if start is not None and t2 < start:
            continue
        if end is not None and t1 > end:
            continue

        records.append(record)

    return records
