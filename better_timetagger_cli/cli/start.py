from time import time

import click

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.utils import generate_uid, print_records


@click.command(("start", "check-in", "in"))
@click.option(
    "-d",
    "--description",
    type=click.STRING,
    help="Add a description to the task.",
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
@click.argument("tags", type=click.STRING, nargs=-1)
def start(tags: list[str], description: str, empty: bool, keep: bool) -> None:
    """
    Start time tracking.

    Provide one or more tags to label the task.

    Command aliases: 'check-in', 'in'
    """
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]
    description = f"{' '.join(tags)} {description}".strip()

    if not description and not empty:
        abort("No tags or description provided. Use -e to start an empty task.")

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
                abort("Timer with this description is already running.")
            r["t2"] = now
        put_records([new_record, *running_records])
        print_records(started=[new_record], stopped=running_records)
