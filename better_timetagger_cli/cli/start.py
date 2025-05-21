from time import time

import click

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.utils import generate_uid, print_records


@click.command()
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    help="Keep previous tasks running, do not stop them.",
)
@click.option(
    "-t",
    "--tag",
    type=click.STRING,
    multiple=True,
    help="Apply tags to the task. Can be used multiple times. Alternatively, add tags using '#' in the description.",
)
@click.argument("description", type=click.STRING, nargs=-1)
def start(keep: bool, tag: list[str], description: list[str]) -> None:
    """
    Start timer with the given description.
    """
    tags = [f"#{t}" if not t.startswith("#") else t for t in tag]
    description_string = f"{' '.join(description)} {' '.join(tags)}"

    now = int(time())
    new_record = {
        "key": generate_uid(),
        "t1": now,
        "t2": now,
        "mt": now,
        "st": 0,
        "ds": description_string,
    }
    running_records = get_runnning_records()["records"]

    if keep:
        put_records([new_record])
        print_records(started=[new_record], running=running_records)

    else:
        for r in running_records:
            if r.get("ds", "") == description_string:
                abort("Timer with this description is already running.")
            r["t2"] = now
        put_records([new_record, *running_records])
        print_records(started=[new_record], stopped=running_records)
