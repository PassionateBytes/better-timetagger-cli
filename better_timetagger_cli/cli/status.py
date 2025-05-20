from datetime import datetime, timedelta
from time import time

import click

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.utils import print_records, readable_duration, total_time


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
    click.echo()
    click.echo(f"Total hours this month: {readable_duration(total_month)}")
    click.echo(f"Total hours this week: {readable_duration(total_week)}")
    click.echo(f"Total hours today: {readable_duration(total_day)}")
    click.echo()
    if not running_records:
        click.echo("Running: N/A")
    elif len(running_records) == 1:
        r = running_records[0]
        duration = now - running_records[0]["t1"]
        click.echo(f"Running: {readable_duration(duration)} - {r.get('ds')}")
    else:
        click.echo(f"There are {len(running_records)} running timers.")
    click.echo()
    click.echo("Todays records:")
    print_records(day_records)
