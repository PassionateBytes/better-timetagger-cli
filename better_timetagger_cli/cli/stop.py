from time import time

import click

from better_timetagger_cli.lib.api import get_runnning_records, put_records
from better_timetagger_cli.lib.click_utils import abort
from better_timetagger_cli.lib.utils import print_records


@click.command(("stop", "check-out", "out"))
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
)
def stop(tags: list[str]) -> None:
    """
    Stop time tracking.

    If tags are provided, all running records will be stopped.
    Specify one or more tags to stop only matching records.

    Command aliases: 'check-out', 'out'
    """
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]

    running_records = get_runnning_records()["records"]
    if not running_records:
        abort("No running records.")

    still_running_records = []
    stopped_records = []
    now = int(time())

    for r in running_records:
        if tags and not any(tag in r["ds"] for tag in tags):
            still_running_records.append(r)
        else:
            r["t2"] = now
            stopped_records.append(r)

    put_records(stopped_records)
    print_records(stopped=stopped_records, running=still_running_records)
