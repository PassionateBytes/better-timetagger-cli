from datetime import datetime, timedelta
from time import time

import click
from rich import print
from rich.box import SIMPLE
from rich.prompt import IntPrompt
from rich.table import Table

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.utils import highlight_tags_in_description

from .start import start


@click.command()
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
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
@click.pass_context
def resume(ctx: click.Context, tags: list[str], keep: bool, select: bool) -> None:
    """
    Start time tracking, using the same tags and description as the most recent record.

    Specify a tag to resume the most recent record matching that tag.

    Note that only records from the last 4 weeks are considered.
    """
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]

    now = int(time())
    now_dt = datetime.fromtimestamp(now)
    today = datetime(now_dt.year, now_dt.month, now_dt.day)
    tomorrow = today + timedelta(days=1)
    last_month = today - timedelta(weeks=4)
    t1 = int(last_month.timestamp())
    t2 = int(tomorrow.timestamp())

    records = get_records(t1, t2)["records"]
    records = [r for r in records if all(t in r["ds"] for t in tags)]
    records.sort(key=lambda r: r["t2"], reverse=True)

    if len(records) == 0:
        abort("No matching records within the last week.")
        return

    # Unless using 'select' mode, resume the most recent matching record
    if not select or len(records) == 1:
        resume_description = records[0]["ds"]

    # Otherwise prompt the user to select a record
    else:
        list_records = []
        for r in records:
            if any(r["ds"].strip() == ur["ds"].strip() for ur in list_records):
                continue
            list_records.append(r)
            if len(list_records) >= 10:
                break

        table = Table(show_header=False, box=SIMPLE)
        table.add_column(justify="left", style="cyan")
        table.add_column(justify="left", style="magenta")
        for i, r in enumerate(list_records):
            table.add_row(f"{'' if i else '[bold]'}[{i}]:", highlight_tags_in_description(r["ds"]))
        print(table)

        selected = None
        while selected is None:
            selected = IntPrompt.ask("Select task to resume", choices=[str(i) for i in range(len(list_records))], show_choices=False, default=0)
        resume_description = list_records[int(selected)]["ds"]

    ctx.invoke(start, description=resume_description.strip(), keep=keep)
