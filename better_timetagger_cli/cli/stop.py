from time import time
from typing import Literal

import click
import dateparser

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.utils import abort, print_records, unify_tags_callback


@click.command(("stop", "check-out", "out"))
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=unify_tags_callback,
)
@click.option(
    "-a",
    "--at",
    type=click.STRING,
    help="Stop the task at a specific time. Supports natural language.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="all",
    help="Tag matching mode. Filter records that match any or all tags. Default: all.",
)
def stop(tags: list[str], at: str | None, tags_match: Literal["any", "all"]) -> None:
    """
    Stop time tracking.

    If tags are provided, all running records will be stopped.
    Specify one or more tags to stop only matching records.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'check-out', 'out'
    """
    running_records = get_runnning_records()["records"]
    if not running_records:
        abort("No running records.")

    still_running_records = []
    stopped_records = []

    now = int(time())
    if at:
        at_dt = dateparser.parse(at)
        if not at_dt:
            abort("Could not parse '--at'.")
        stop_t = int(at_dt.timestamp())
    else:
        stop_t = now

    for r in running_records:
        if tags:
            match_func = any if tags_match == "any" else all
            if not match_func(tag in r["ds"] for tag in tags):
                still_running_records.append(r)
        else:
            r["t2"] = stop_t
            r["mt"] = stop_t
            stopped_records.append(r)

    put_records(stopped_records)
    print_records(stopped=stopped_records, running=still_running_records)
