"""
### Input Parsing & Validation

Functions that parse user input and validate data
"""

from datetime import datetime

import click
import parsedatetime  # type: ignore[import-untyped]

from .output import abort


def tags_callback(ctx: click.Context, param: click.Parameter, tags: list[str]) -> list[str]:
    """
    Click argument callback to normalize tags.

    Ensure tags start with '#' and remove duplicates.

    Args:
        tags: A list of tags.

    Returns:
        A list of unique tags.
    """
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]
    tags = list(set(tags))
    return tags


def parse_datetime(input: str) -> datetime:
    """
    Parse natural language date and time input.

    Args:
        input: A string representing the date and time.

    Returns:
        A datetime object representing the parsed date and time.
    """

    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)
    parsed, parse_ctx = cal.parse(input)

    # only date parsed -> set time to 00:00:00
    if parse_ctx.hasDate and not parse_ctx.hasTime:
        return datetime(
            year=parsed.tm_year,
            month=parsed.tm_mon,
            day=parsed.tm_mday,
            hour=0,
            minute=0,
            second=0,
        )

    # only time parsed -> set date to today
    elif not parse_ctx.hasDate and parse_ctx.hasTime:
        today = datetime.today()
        return datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=parsed.tm_hour,
            minute=parsed.tm_min,
            second=parsed.tm_sec,
        )

    # date and time parsed
    elif parse_ctx.hasDate and parse_ctx.hasTime:
        return datetime(
            year=parsed.tm_year,
            month=parsed.tm_mon,
            day=parsed.tm_mday,
            hour=parsed.tm_hour,
            minute=parsed.tm_min,
            second=parsed.tm_sec,
        )

    else:
        abort(f"Could not parse input: {input}")


def parse_start_end(
    start: str | None,
    end: str | None,
) -> tuple[datetime, datetime]:
    """
    Parse the time frame for the show or export command.

    Args:
        start: Start date and time for the records.
        end: End date and time for the records.

    Returns:
        A tuple containing the start and end date and time.
    """
    start_dt = parse_datetime(start) if start else datetime(2000, 1, 1)
    end_dt = parse_datetime(end) if end else datetime(3000, 1, 1)

    return start_dt, end_dt


def parse_at(at: str | None) -> int | None:
    """
    Parse the 'at' parameter.

    Args:
        at: The 'at' parameter value.

    Returns:
        The parsed start time as a timestamp, or None if not provided.
    """
    if at:
        at_dt = parse_datetime(at)
        return int(at_dt.timestamp())

    return None
