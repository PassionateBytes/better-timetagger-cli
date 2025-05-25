
import click
from rich.console import Group

from better_timetagger_cli.lib.api import create_record_key, get_runnning_records, put_records
from better_timetagger_cli.lib.misc import abort, now_timestamp
from better_timetagger_cli.lib.output import print_records, render_records
from better_timetagger_cli.lib.parsers import parse_at, tags_callback
from better_timetagger_cli.lib.types import Record


@click.command(("start", "check-in", "in"))  # type: ignore[call-overload]
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
@click.option(
    "-v",
    "--show-keys",
    is_flag=True,
    help="List each record's key.",
)
def start_cmd(
    tags: list[str],
    at: str | None,
    description: str,
    empty: bool,
    keep: bool,
    show_keys: bool,
) -> None:
    """
    Start time tracking.

    Provide one or more tags to label the task.

    By default, previous tasks will be stopped automatically.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    Command aliases: 'start', 'check-in', 'in'
    """
    description = f"{' '.join(tags)} {description}".strip()

    if not description and not empty:
        abort("No tags or description provided. Use '--empty' to start a task without tags or description.")

    now = now_timestamp()
    start_t = parse_at(at) or now
    new_record: Record = {
        "key": create_record_key(),
        "t1": start_t,
        "t2": start_t,
        "mt": now,
        "st": 0,
        "ds": description,
    }

    running_records = get_runnning_records()["records"]
    stopped_records = []

    for r in running_records.copy():
        # Avoid starting duplicate task
        if r["ds"] == description:
            abort(
                Group(
                    "\n[red]Task with these tags and description is already running.[/red]",
                    render_records(running=running_records, show_keys=show_keys),
                )
            )

        # Stop running tasks, unless in 'keep' mode
        if not keep:
            r["t2"] = now
            r["mt"] = now
            stopped_records.append(r)
            running_records.remove(r)

    put_records([new_record, *stopped_records])
    print_records(started=[new_record], running=running_records, stopped=stopped_records, show_keys=show_keys)
