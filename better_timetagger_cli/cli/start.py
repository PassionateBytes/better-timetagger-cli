from time import time

import click
import dateparser
from rich import print

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.types import Record
from better_timetagger_cli.lib.utils import abort, generate_uid, print_records, unify_tags_callback


@click.command(("start", "check-in", "in"))
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
    help="Start the task at a specific time. Supports natural language.",
)
@click.option(
    "-d",
    "--description",
    type=click.STRING,
    help="Add a description to the task.",
    default="",
)
@click.option(
    "-e",
    "--empty",
    is_flag=True,
    help="Allow starting a task without tags or description.",
)
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    help="Keep previous tasks running, do not stop them.",
)
def start(tags: list[str], at: str | None, description: str, empty: bool, keep: bool) -> None:
    """
    Start time tracking.

    Provide one or more tags to label the task.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'check-in', 'in'
    """
    description = f"{' '.join(tags)} {description}".strip()

    if not description and not empty:
        abort("No tags or description provided. Use -e to start an empty task.")

    now = int(time())
    if at:
        at_dt = dateparser.parse(at)
        if not at_dt:
            abort("Could not parse '--at'.")
        start_t = int(at_dt.timestamp())
    else:
        start_t = now

    new_record: Record = {
        "key": generate_uid(),
        "t1": start_t,
        "t2": start_t,
        "mt": now,
        "st": 0,
        "ds": description,
    }
    running_records = get_runnning_records()["records"]

    if keep:
        put_records([new_record])
        print_records(started=[new_record], running=running_records)

    else:
        for r in running_records:
            if r.get("ds", "") == description:
                print("\n[red]Task with these tags and description is already running.[/red]")
                print_records(running=running_records)
                exit(1)

            r["t2"] = now
        put_records([new_record, *running_records])
        print_records(started=[new_record], stopped=running_records)
