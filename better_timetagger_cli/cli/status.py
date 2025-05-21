from datetime import datetime, timedelta
from time import time

import click
from rich import print
from rich.box import SIMPLE
from rich.table import Table

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.utils import readable_duration, styled_padded, total_time


@click.command()
def status() -> None:
    """
    Get an overview of today, this week and this month.
    """

    now = int(time())
    d = datetime.fromtimestamp(now)

    # Relevant dates
    today = datetime(d.year, d.month, d.day)
    tomorrow = today + timedelta(1)
    last_monday = today - timedelta(today.weekday())
    next_monday = last_monday + timedelta(7)
    first_of_this_month = datetime(d.year, d.month, 1)
    first_of_next_month = datetime(d.year, d.month + 1, 1) if d.month < 12 else datetime(d.year + 1, 1, 1)

    # Convert to timestamps
    t_day1 = int(today.timestamp())
    t_day2 = int(tomorrow.timestamp())
    t_week1 = int(last_monday.timestamp())
    t_week2 = int(next_monday.timestamp())
    t_month1 = int(first_of_this_month.timestamp())
    t_month2 = int(first_of_next_month.timestamp())

    # Collect records
    records = get_records(t_month1, t_month2)["records"]
    month_records = [r for r in records if not r.get("ds", "").startswith("HIDDEN")]
    week_records = [r for r in month_records if r["t1"] < t_week2 and (r["t1"] == r["t2"] or r["t2"] > t_week1)]
    day_records = [r for r in week_records if r["t1"] < t_day2 and (r["t1"] == r["t2"] or r["t2"] > t_day1)]
    running_records = [r for r in week_records if r["t1"] == r["t2"]]

    # Calculate totals
    total_month = total_time(month_records, first_of_this_month, first_of_next_month)
    total_week = total_time(week_records, last_monday, next_monday)
    total_day = total_time(day_records, today, tomorrow)

    # Report
    table = Table(show_header=False, box=SIMPLE)
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(justify="left", style="magenta")
    table.add_row("Total this month:", readable_duration(total_month))
    table.add_row("Total this week:", readable_duration(total_week))
    table.add_row("Total today:", readable_duration(total_day))
    table.add_section()
    table.add_row("Records this month:", styled_padded(len(month_records)))
    table.add_row("Records this week:", styled_padded(len(week_records)))
    table.add_row("Records today:", styled_padded(len(day_records)))
    table.add_section()
    table.add_row("Running:", styled_padded(len(running_records)))
    print(table)
