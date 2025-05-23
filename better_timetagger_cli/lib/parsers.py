from datetime import datetime

import click
import dateparser

from .misc import abort


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
    start_dt = dateparser.parse(start) if start is not None else datetime(2000, 1, 1)
    end_dt = dateparser.parse(end) if end is not None else datetime(3000, 1, 1)

    if start_dt is None:
        abort("Could not parse '--start'.")
    if end_dt is None:
        abort("Could not parse '--end'.")

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
        at_dt = dateparser.parse(at)
        if not at_dt:
            abort("Could not parse '--at'.")
        return int(at_dt.timestamp())
    return None
