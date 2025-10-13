from datetime import datetime, timedelta
from typing import Literal

import click
from rich.prompt import IntPrompt

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.cli import AliasedCommand
from better_timetagger_cli.lib.output import abort, print_records
from better_timetagger_cli.lib.parsing import tags_callback
from better_timetagger_cli.lib.timestamps import now_timestamp
from better_timetagger_cli.lib.types import Record

from .start_cmd import start_cmd


@click.command(
    "resume",
    aliases=("r",),
    cls=AliasedCommand,
)
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
    "-k",
    "--keep",
    is_flag=True,
    help="Keep previous tasks running, do not stop them automatically.",
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
@click.pass_context
def resume_cmd(
    ctx: click.Context,
    tags: list[str],
    at: str | None,
    keep: bool,
    select: bool,
    show_keys: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    Start time tracking, using the same tags and description of a recent record.

    You may specify a tag, to only resume the most recent record that matches the tag.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.

    By default, currently running tasks will be stopped automatically. Use '--keep' to keep them running.

    Note that only records from the last 4 weeks are considered.
    """
    now = now_timestamp()
    now_dt = datetime.fromtimestamp(now)
    today = datetime(now_dt.year, now_dt.month, now_dt.day)
    tomorrow = today + timedelta(days=1)
    last_month = today - timedelta(weeks=4)

    records = get_records(
        last_month,
        tomorrow,
        tags=tags,
        tags_match=tags_match,
    )["records"]

    if not records:
        abort("No records found within last 4 weeks.")
        return

    # Resume most recent record
    if not select:
        resume_description = records[0]["ds"].strip()
        ctx.invoke(start_cmd, description=resume_description, at=at, keep=keep, show_keys=show_keys)
        return

    # In 'select' mode, provide choice of records to resume
    else:
        resume_record_choices: list[Record] = []
        for r in records:
            # avoid duplicate descriptions
            if any(r["ds"].strip() == choice["ds"].strip() for choice in resume_record_choices):
                continue
            resume_record_choices.append(r)
            # max 10 choices
            if len(resume_record_choices) >= 10:
                break

        # prompt for choice
        print_records(resume_record_choices, show_index=True, show_keys=show_keys)

        # prompt for choice
        selected = None
        while selected is None:
            selected = IntPrompt.ask(
                "Select task to resume",
                choices=[str(i) for i in range(len(resume_record_choices))],
                show_choices=False,
                default=0,
            )

        resume_description = resume_record_choices[int(selected)]["ds"].strip()
        ctx.invoke(start_cmd, description=resume_description, at=at, keep=keep, show_keys=show_keys)
