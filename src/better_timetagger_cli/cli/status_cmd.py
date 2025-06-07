from datetime import datetime, timedelta

import click
from rich.box import SIMPLE
from rich.table import Table

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.console import console
from better_timetagger_cli.lib.misc import now_timestamp
from better_timetagger_cli.lib.output import readable_duration, styled_padded
from better_timetagger_cli.lib.records import get_tag_stats, get_total_time


@click.command()
def status_cmd() -> None:
    """
    Get an overview of today, this week and this month.

    Command aliases: 'status'
    """

    # Relevant dates
    now = now_timestamp()
    now_dt = datetime.fromtimestamp(now)
    today = datetime(now_dt.year, now_dt.month, now_dt.day)
    tomorrow = today + timedelta(1)
    last_monday = today - timedelta(today.weekday())
    next_monday = last_monday + timedelta(7)
    first_of_this_month = datetime(now_dt.year, now_dt.month, 1)
    first_of_next_month = datetime(now_dt.year, now_dt.month + 1, 1) if now_dt.month < 12 else datetime(now_dt.year + 1, 1, 1)

    # Convert to timestamps
    t_day1 = int(today.timestamp())
    t_day2 = int(tomorrow.timestamp())
    t_week1 = int(last_monday.timestamp())
    t_week2 = int(next_monday.timestamp())

    # Collect records
    month_records = get_records(first_of_this_month, first_of_next_month)["records"]
    week_records = [r for r in month_records if r["t1"] < t_week2 and (r["t1"] == r["t2"] or r["t2"] > t_week1)]
    day_records = [r for r in week_records if r["t1"] < t_day2 and (r["t1"] == r["t2"] or r["t2"] > t_day1)]
    running_records = [r for r in week_records if r["t1"] == r["t2"]]

    # Calculate totals
    total_month = get_total_time(month_records, first_of_this_month, first_of_next_month)
    total_week = get_total_time(week_records, last_monday, next_monday)
    total_day = get_total_time(day_records, today, tomorrow)

    # Get tag totals
    month_tag_stats = get_tag_stats(month_records)
    week_tag_stats = get_tag_stats(week_records)
    day_tag_stats = get_tag_stats(day_records)
    running_tag_stats = get_tag_stats(running_records)

    records_padding_length = max(len(str(len(month_records))), 5)

    # Report
    table = Table(show_header=False, box=SIMPLE)
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(justify="left", style="magenta", no_wrap=True)
    table.add_column(justify="left", style="green")
    table.add_row(
        "Total this month:",
        readable_duration(total_month),
        ", ".join(f"{tag} [dim]({readable_duration(duration)})[/dim]" for tag, (_, duration) in month_tag_stats.items()),
    )
    table.add_row(
        "Total this week:",
        readable_duration(total_week),
        ", ".join(f"{tag} [dim]({readable_duration(duration)})[/dim]" for tag, (_, duration) in week_tag_stats.items()),
    )
    table.add_row(
        "Total today:",
        readable_duration(total_day),
        ", ".join(f"{tag} [dim]({readable_duration(duration)})[/dim]" for tag, (_, duration) in day_tag_stats.items()),
    )
    table.add_section()
    table.add_row(
        "Records this month:",
        styled_padded(len(month_records), records_padding_length),
        ", ".join(f"{tag} [dim]({count})[/dim]" for tag, (count, _) in month_tag_stats.items()),
    )
    table.add_row(
        "Records this week:",
        styled_padded(len(week_records), records_padding_length),
        ", ".join(f"{tag} [dim]({count})[/dim]" for tag, (count, _) in week_tag_stats.items()),
    )
    table.add_row(
        "Records today:",
        styled_padded(len(day_records), records_padding_length),
        ", ".join(f"{tag} [dim]({count})[/dim]" for tag, (count, _) in day_tag_stats.items()),
    )
    table.add_section()
    table.add_row(
        "Running:",
        styled_padded(len(running_records), records_padding_length),
        ", ".join(list(running_tag_stats)),
    )
    console.print(table)
