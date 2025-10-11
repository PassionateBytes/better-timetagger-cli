from typing import Literal

import click
from rich.live import Live

from better_timetagger_cli.lib.api import continuous_updates, get_records, get_running_records
from better_timetagger_cli.lib.cli import AliasedCommand
from better_timetagger_cli.lib.console import abort, console
from better_timetagger_cli.lib.output import render_records_with_summary
from better_timetagger_cli.lib.parsing import parse_start_end, tags_callback
from better_timetagger_cli.lib.records import round_records
from better_timetagger_cli.lib.timestamps import now_timestamp


@click.command(
    "show",
    aliases=("display", "ls", "s", "d"),
    cls=AliasedCommand,
)
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=tags_callback,
)
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    help="Include only records later than this time. Supports natural language.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Include only records earlier than this time. Supports natural language.",
)
@click.option(
    "-r",
    "--round",
    is_flag=False,
    flag_value=5,
    type=click.IntRange(min=1),
    help="Round record times to a regular interval in minutes. Specify a value to round to that number of minutes (e.g., '--round 10' for 10 minutes). If used as a flag without a value (e.g., '--round'), defaults to 5 minutes.",
)
@click.option(
    "-H",
    "--hidden",
    is_flag=True,
    help="Include only hidden (i.e. removed) records in the output.",
)
@click.option(
    "-R",
    "--running",
    is_flag=True,
    help="Include only running records in the output.",
)
@click.option(
    "-z",
    "--summary",
    "summary",
    flag_value=True,
    default=None,
    help="Show only the summary, disable table.",
)
@click.option(
    "-Z",
    "--no-summary",
    "summary",
    flag_value=False,
    default=None,
    help="Show only the table, disable summary.",
)
@click.option(
    "-f",
    "--follow",
    is_flag=True,
    help="Continuously monitor for changes and update the output in real time. If used with a relative '--start' time (like '2 hours ago'), the monitored time frame will follow the current time.",
)
@click.option(
    "-v",
    "--show-keys",
    is_flag=True,
    help="List each record's unique key. Useful to when you want to remove or restore records.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="any",
    help="Tag matching mode. Include records that match either 'any' or 'all' tags. Default: any.",
)
def show_cmd(
    tags: list[str],
    start: str | None,
    end: str | None,
    round: int | None,
    hidden: bool,
    running: bool,
    summary: bool | None,
    follow: bool,
    show_keys: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    List tasks of the requested time frame.

    If no tags are provided, all tasks within the selected time frame will be shown.
    Specify one or more tags to show only matching tasks.
    Tags can be entered without the leading hashtag '#'.

    The parameters '--start' and '--end' support natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.
    """
    if running and (start or end):
        abort("The '--running' option cannot be used with '--start' or '--end'.")

    start_dt, end_dt = parse_start_end(start, end)

    # Regular one-time output
    if not follow:
        if not running:
            records = get_records(
                start_dt,
                end_dt,
                tags=tags,
                tags_match=tags_match,
                hidden=hidden,
            )["records"]
        else:
            records = get_running_records(
                tags=tags,
                tags_match=tags_match,
                hidden=hidden,
            )["records"]

        if not records:
            abort("No records found.")

        if round:
            records = round_records(records, round)

        output = render_records_with_summary(records, summary=summary, start_dt=start_dt, end_dt=end_dt, show_keys=show_keys)
        console.print(output)

    # In 'follow' mode, monitor continuously for changes
    else:
        with Live(console=console) as live:
            for update in continuous_updates(start_dt, tags=tags, tags_match=tags_match, hidden=hidden, running=running):
                # Re-evaluate time frame and filter cached records accordingly to support "floating" time frames
                start_dt, end_dt = parse_start_end(start, end)
                start_timestamp = start_dt.timestamp()
                update["records"] = [r for r in update["records"] if start_timestamp <= r["t2"] or r["_running"]]

                if round:
                    update["records"] = round_records(update["records"], round)

                if update["records"]:
                    output = render_records_with_summary(update["records"], summary=summary, start_dt=start_dt, end_dt=now_timestamp(), show_keys=show_keys)
                    live.update(output)
                else:
                    live.update("\n[yellow]Waiting for records...[/yellow]\n")
