from time import time

import click
from rich.box import SIMPLE
from rich.table import Table

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.rich_utils import console
from better_timetagger_cli.lib.utils import generate_uid, readable_duration, readable_time


@click.command()
@click.argument("description", type=click.STRING, nargs=-1)
def start(description: list[str] | str) -> None:
    """
    Start timer with the given description.
    Use hashes ('#') in your description to add tags.
    """
    now = int(time())
    if not isinstance(description, str):
        description = " ".join(description)

    new_record = {
        "key": generate_uid(),
        "t1": now,
        "t2": now,
        "mt": now,
        "st": 0,
        "ds": description,
    }

    running_records = get_runnning_records()["records"]

    for r in running_records:
        if r.get("ds", "") == description:
            console.print("[red]Timer with this description is already running.[/red]")
            raise click.Abort

        r["t2"] = now

    put_records([new_record, *running_records])

    # Report
    table = Table(box=SIMPLE)
    table.add_column("Started", justify="right")
    table.add_column("Stopped", justify="left")
    table.add_column("Duration", justify="left")
    table.add_column("Description", justify="left")
    table.add_row(readable_time(now), "...", "...", description, style="green")
    for r in running_records:
        table.add_row(readable_time(r["t1"]), readable_time(r["t2"]), readable_duration(r["t2"] - r["t1"]), r["ds"], style="dim red")
    console.print(table)
