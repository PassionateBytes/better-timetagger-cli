from datetime import datetime
from typing import Literal

import click
from rich.box import SIMPLE
from rich.console import Group
from rich.live import Live
from rich.table import Table

from better_timetagger_cli.lib.api import continuous_updates, get_records
from better_timetagger_cli.lib.console import console
from better_timetagger_cli.lib.misc import abort
from better_timetagger_cli.lib.output import readable_duration, render_records, styled_padded
from better_timetagger_cli.lib.parsers import parse_start_end, tags_callback
from better_timetagger_cli.lib.records import get_tag_stats, get_total_time
from better_timetagger_cli.lib.types import Record


@click.command(("show", "report", "display"))  # type: ignore[call-overload]
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
    help="Show records later than this time. Supports natural language.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Show records earlier than this time. Supports natural language.",
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
    "-f",
    "--follow",
    is_flag=True,
    help="Continuously monitor for changes and update the output in real time. If used with a relative '--start' time (like '2 hours ago'), the moniroted time frame will follow the current time.",
)
@click.option(
    "-v",
    "--show-keys",
    is_flag=True,
    help="List each record's key.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="any",
    help="Tag matching mode. Filter records that match any or all tags. Default: any.",
)
def show_cmd(
    tags: list[str],
    start: str | None,
    end: str | None,
    summary: bool | None,
    follow: bool,
    show_keys: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    List tasks of the requested time frame.

    If no tags are provided, all tasks within the selected time frame will be shown.
    Specify one or more tags to show only matching tasks.

    The parameters '--start' and '--end' support natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'show', 'report', 'display'
    """
    start_dt, end_dt = parse_start_end(start, end)

    # Regular one-time output
    if not follow:
        records = get_records(
            start_dt,
            end_dt,
            tags=tags,
            tags_match=tags_match,
        )["records"]

        if not records:
            abort("No records found.")

        console.print(render_output(summary, records, start_dt, end_dt, show_keys))

    # In 'follow' mode, monitor continuously for changes
    else:
        waiting_msg = "\n[red]Waiting for records...[/red]\n"
        with Live(waiting_msg) as live:
            for update in continuous_updates(start_dt, tags=tags, tags_match=tags_match):
                # Re-evaluate time frame and filter cached records accordingly to support "floating" time frames
                start_dt, end_dt = parse_start_end(start, end)
                update["records"] = [r for r in update["records"] if start_dt.timestamp() <= r["t1"] or r["t1"] == r["t2"]]

                if update["records"]:
                    live.update(render_output(summary, update["records"], start_dt, update["server_time"], show_keys))
                else:
                    live.update(waiting_msg)


def render_output(summary: bool | None, records: list[Record], start_dt: int | datetime, end_dt: int | datetime, show_keys: bool) -> Group:
    """
    Render the output for the show command.

    Args:
        summary: Flag to indicate whether to show summary or not.
        records: List of records to display.
        start_dt: Start date and time for the records.
        end_dt: End date and time for the records.
        show_keys: Flag to indicate whether to show record keys.

    Returns:
        A rich console group containing the rendered output.
    """
    renderables = []

    if summary is not False:
        renderables.append(render_summary(records, start_dt, end_dt))

    if summary is not True:
        renderables.append(render_records(records, show_keys=show_keys))

    return Group(*renderables)


def render_summary(records: list[Record], start_dt: int | datetime, end_dt: int | datetime) -> Table:
    """
    Use rich to render a summary of the records.

    Args:
        records: List of records to summarize.
        start_dt: Start date and time for the summary.
        end_dt: End date and time for the summary.

    Returns:
        Table: A rich table object containing the summary.
    """
    total = get_total_time(records, start_dt, end_dt)
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
        for tag, (count, duration) in tag_stats.items():
            table.add_row(
                f"[green]{tag}:[/green]",
                styled_padded(count, records_padding_length),
                readable_duration(duration),
            )

    return table
