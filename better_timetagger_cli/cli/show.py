from datetime import datetime, timedelta
from typing import Literal

import click
import dateparser
from rich import print
from rich.box import SIMPLE
from rich.table import Table

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.types import Record
from better_timetagger_cli.lib.utils import abort, get_tag_stats, readable_duration, render_records, styled_padded, total_time, unify_tags_callback


@click.command(("show", "report", "display"))
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=unify_tags_callback,
)
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    help="Show records later than this time. Supports natural language.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Show records earlier than this time. Supports natural language.",
)
@click.option(
    "-d",
    "--days",
    type=click.IntRange(min=1),
    help="Number of recent days to display. Can not be used with '--start' or '--end'.",
)
@click.option(
    "-z",
    "--summary",
    "summary",
    flag_value=True,
    default=None,
    help="Show summary only, disable table.",
)
@click.option(
    "-Z",
    "--no-summary",
    "summary",
    flag_value=False,
    default=None,
    help="Show table only, disable summary.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="any",
    help="Tag matching mode. Filter records that match [any] or [all] tags.",
)
def show(
    tags: list[str],
    start: str | None,
    end: str | None,
    days: int | None,
    summary: bool | None,
    tags_match: Literal["any", "all"],
) -> None:
    """
    List tasks of the requested time frame.

    The parameters '--start' and '--end' support natural language.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'report', 'display'
    """
    if days is not None and (start is not None or end is not None):
        abort("Can not combine '--days' parameter with either '--start' or '--end'.")

    # 'days' mode
    elif days is not None:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    # 'start' and 'end' mode
    else:
        start_dt = dateparser.parse(start) if start is not None else datetime(2000, 1, 1)
        end_dt = dateparser.parse(end) if end is not None else datetime(3000, 1, 1)
        if start_dt is None:
            abort("Could not parse '--start' date.")
        if end_dt is None:
            abort("Could not parse '--end' date.")

    records = get_records(
        start_dt,
        end_dt,
        tags=tags,
        tags_match=tags_match,
    )["records"]

    if not records:
        abort("No matching records.")

    if summary is not False:
        print_summary(records, start_dt, end_dt)

    if summary is not True:
        print_records(records)


def print_summary(records: list[Record], start_dt: datetime, end_dt: datetime) -> None:
    """
    Print a summary of the records.

    Args:
        records (list[Record]): List of records to summarize.
        start_dt (datetime): Start date and time for the summary.
        end_dt (datetime): End date and time for the summary.
    """
    total = total_time(records, start_dt, end_dt)
    tag_stats = get_tag_stats(records)

    records_padding_length = max(len(str(len(records))), 5)

    table = Table(show_header=False, box=SIMPLE)
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="magenta", no_wrap=True)
    table.add_column(style="magenta", no_wrap=True)

    table.add_row(
        "Total:",
        styled_padded(len(records), records_padding_length),
        readable_duration(total),
        style="bold",
    )

    if tag_stats:
        table.add_section()
        for tag, (count, duration) in tag_stats.items():
            table.add_row(
                f"[green]{tag}:[/green]",
                styled_padded(count, records_padding_length),
                readable_duration(duration),
            )

    print(table)
