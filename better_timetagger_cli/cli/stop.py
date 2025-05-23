from typing import Literal

import click

from better_timetagger_cli.cli.start import parse_at
from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.click import tags_callback
from better_timetagger_cli.lib.misc import abort, now_timestamp
from better_timetagger_cli.lib.output import print_records
from better_timetagger_cli.lib.records import check_record_tags_match


@click.command(("stop", "check-out", "out"))  # type: ignore[call-overload]
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=tags_callback,
)
@click.option(
    "-a",
    "--at",
    type=click.STRING,
    help="Stop the task at a specific time. Supports natural language.",
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
    default="all",
    help="Tag matching mode. Filter records that match any or all tags. Default: all.",
)
def stop(tags: list[str], at: str | None, show_keys: bool, tags_match: Literal["any", "all"]) -> None:
    """
    Stop time tracking.

    If tags are provided, all running records will be stopped.
    Specify one or more tags to stop only matching records.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'stop', 'check-out', 'out'
    """
    running_records = get_runnning_records()["records"]
    stopped_records = []

    if not running_records:
        abort("No running records.")

    now = now_timestamp()
    stop_t = parse_at(at) or now

    for r in running_records.copy():
        # Stop running tasks with matching tags
        if check_record_tags_match(r, tags, tags_match):
            r["t2"] = stop_t
            r["mt"] = stop_t
            stopped_records.append(r)
            running_records.remove(r)

    put_records(stopped_records)
    print_records(stopped=stopped_records, running=running_records, show_keys=show_keys)
