from datetime import datetime, timedelta
from typing import Literal

import click
from rich.box import SIMPLE
from rich.prompt import IntPrompt
from rich.table import Table
from rich.text import Text

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.console import console
from better_timetagger_cli.lib.misc import abort, now_timestamp
from better_timetagger_cli.lib.output import highlight_tags_in_description
from better_timetagger_cli.lib.parsers import tags_callback

from .start_cmd import start_cmd


@click.command()
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
    help="Keep previous tasks running, do not stop them.",
)
@click.option(
    "-s",
    "--select",
    is_flag=True,
    help="List matching records to select from, if multiple different records match.",
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
    help="Tag matching mode. Find records that match any or all tags. Default: all.",
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
    Start time tracking, using the same tags and description a recent record.

    You may specify a tag, to only resume the most recent record that matches the tag.

    The '--at' parameter supports natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.


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
        sort_by="t2",
        sort_reverse=True,
    )["records"]

    if not records:
        abort("No records found within last 4 weeks.")
        return

    # Resume most recent record
    if not select or len(records) == 1:
        resume_description = records[0]["ds"].strip()
        ctx.invoke(start_cmd, description=resume_description, at=at, keep=keep, show_keys=show_keys)
        return

    # In 'select' mode, provide choice of records to resume
    else:
        resume_description_choices: list[str] = []
        for r in records:
            # avoid duplicates
            if any(r["ds"].strip() == choice for choice in resume_description_choices):
                continue
            resume_description_choices.append(r["ds"].strip())
            # max 10 choices
            if len(resume_description_choices) >= 10:
                break

        # print choices
        table = Table(show_header=False, box=SIMPLE)
        table.add_column(style="cyan")
        table.add_column(style="magenta")
        for i, choice in enumerate(resume_description_choices):
            id = Text(f"[{i}]:", style="bold" if i <= 0 else "dim")
            table.add_row(id, highlight_tags_in_description(choice))
        console.print(table)

        # prompt for choice
        selected = None
        while selected is None:
            selected = IntPrompt.ask(
                "Select task to resume",
                choices=[str(i) for i in range(len(resume_description_choices))],
                show_choices=False,
                default=0,
            )

        resume_description = resume_description_choices[int(selected)]
        ctx.invoke(start_cmd, description=resume_description, at=at, keep=keep, show_keys=show_keys)
