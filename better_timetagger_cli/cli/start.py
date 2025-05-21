from time import time

import click
from rich import print

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.utils import generate_uid, print_records


@click.command()
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    help="Keep previous tasks running, do not stop them.",
)
@click.argument("description", type=click.STRING, nargs=-1)
def start(keep: bool, description: list[str] | str) -> None:
    """
    Start timer with the given description.
    Use hashes ('#') in your description to add tags.
    """
    if not isinstance(description, str):
        description = " ".join(description)

    now = int(time())
    new_record = {
        "key": generate_uid(),
        "t1": now,
        "t2": now,
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
                print("[red]Timer with this description is already running.[/red]")
                raise click.Abort
            r["t2"] = now
        put_records([new_record, *running_records])
        print_records(started=[new_record], stopped=running_records)
