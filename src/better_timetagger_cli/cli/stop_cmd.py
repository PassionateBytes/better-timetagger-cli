from typing import Literal

import click
from rich.prompt import IntPrompt

from better_timetagger_cli.lib.api import get_running_records, put_records
from better_timetagger_cli.lib.cli import AliasedCommand
from better_timetagger_cli.lib.console import abort
from better_timetagger_cli.lib.output import print_records
from better_timetagger_cli.lib.parsing import parse_at, tags_callback
from better_timetagger_cli.lib.records import check_record_tags_match, post_process_records
from better_timetagger_cli.lib.timestamps import now_timestamp


@click.command("stop", aliases=("out", "o"), cls=AliasedCommand)
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
    "-S",
    "--select",
    is_flag=True,
    help="Select a record to resume from a list of options.",
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
    default="all",
    help="Tag matching mode. Include records that match either 'any' or 'all' tags. Default: all.",
)
def stop_cmd(
    tags: list[str],
    at: str | None,
    select: bool,
    show_keys: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    Stop time tracking.

    If no tags are provided, all running tasks will be stopped.
    Specify one or more tags to stop only matching tasks.
    Tags can be entered without the leading hashtag '#'.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.
    """
    running_records = get_running_records(
        sort_by="t1",
        sort_reverse=False,
    )["records"]

    now = now_timestamp()
    stop_t = parse_at(at) or now
    stopped_records = []

    # Stop all matching records
    if not select:
        for r in running_records.copy():
            # Stop running tasks with matching tags
            if check_record_tags_match(r, tags, tags_match):
                r["t2"] = stop_t
                r["mt"] = now
                stopped_records.append(r)
                running_records.remove(r)

        if not stopped_records:
            abort("No running records match.")

        stopped_records = post_process_records(stopped_records)

        put_records(stopped_records)
        print_records(running_records, (stopped_records, "red"), show_keys=show_keys)
        return

    # In 'select' mode, provide choice of records to stop
    else:
        stop_record_choices = [r for r in running_records if check_record_tags_match(r, tags, tags_match)]
        print_records(
            stop_record_choices,
            show_index=True,
            show_keys=show_keys,
        )

        selected = None
        while selected is None:
            selected = IntPrompt.ask(
                "Select task to stop",
                choices=[str(i) for i in range(len(stop_record_choices))],
                show_choices=False,
                default=0,
            )

        running_records.remove(stop_record_choices[selected])
        stopped_record = stop_record_choices[selected]
        stopped_record["t2"] = stop_t
        stopped_record["mt"] = now

        put_records(stopped_record)
        print_records(running_records, (stopped_record, "red"), show_keys=show_keys)
