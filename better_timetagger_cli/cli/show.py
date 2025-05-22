from datetime import datetime, timedelta

import click
import dateparser
from rich import print
from rich.box import SIMPLE
from rich.table import Table

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.utils import get_tag_stats, print_records, readable_date_time, readable_duration, total_time


@click.command(("show", "report", "display"))
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    help="Show records later than this time.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Show records earlier than this time.",
)
@click.option(
    "-d",
    "--days",
    type=click.IntRange(min=1),
    help="Number of recent days to display. Can not be used with '--start' or '--end'.",
)
def show(start: str | None, end: str | None, days: int | None) -> None:
    """
    List tasks of the requested time frame.

    The parameters '--start' and '--end' support natural language parsing.
    You can use phrases like 'yesterday', 'May 11', '5 minutes ago', '2025-01-01 12:00', etc.

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

    records = get_records(start_dt, end_dt)["records"]

    # Report Summary
    total = total_time(records, start_dt, end_dt)
    tag_stats = get_tag_stats(records)

    first_record = min(r["t1"] for r in records) if records else None
    running_record = next((datetime.now() for r in records if r["t1"] == r["t2"]), None)
    if running_record:
        last_record = None
    else:
        last_record = max(r["t2"] for r in records) if records else None

    table = Table(show_header=False, box=SIMPLE)
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(justify="left", style="magenta", no_wrap=True)
    table.add_row("Total:", readable_duration(total), style="bold")
    table.add_row("First Record:", readable_date_time(first_record))
    table.add_row("Last Record:", "Currently running" if running_record else readable_date_time(last_record))
    if tag_stats:
        table.add_section()
        for tag, (count, duration) in tag_stats.items():
            table.add_row(f"[green]{tag}:[/green]", f"x{count} ({readable_duration(duration)})")
    print(table)

    # Report Records
    print_records(records)
