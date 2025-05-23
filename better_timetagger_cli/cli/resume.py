from datetime import datetime, timedelta
from time import time
from typing import Literal

import click
from rich import print
from rich.box import SIMPLE
from rich.prompt import IntPrompt
from rich.table import Table
from rich.text import Text

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.utils import abort, highlight_tags_in_description, unify_tags_argument_callback

from .start import start


@click.command()
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=unify_tags_argument_callback,
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
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="all",
    help="Tag matching mode. Filter records that match any or all tags. Default: all.",
)
@click.pass_context
def resume(
    ctx: click.Context,
    tags: list[str],
    keep: bool,
    select: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    Start time tracking, using the same tags and description as the most recent record.

    You may specify a tag, to only resume the most recent record with that specific tag.

    Note that only records from the last 4 weeks are considered.
    """
    now = int(time())
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
        ctx.invoke(start, description=resume_description, keep=keep)
        return

    # In 'select' mode, provide choice of records to resume
    else:
        resume_description_choices = []
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
        print(table)

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
        ctx.invoke(start, description=resume_description, keep=keep)
