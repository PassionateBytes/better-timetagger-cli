import click

from better_timetagger_cli.lib.api import get_updates, put_records
from better_timetagger_cli.lib.misc import abort, now_timestamp
from better_timetagger_cli.lib.output import print_records


@click.command(("restore", "unhide"))  # type: ignore[call-overload]
@click.argument(
    "keys",
    type=click.STRING,
    nargs=-1,
)
def restore_cmd(
    keys: list[str],
) -> None:
    """
    Unhide TimeTagger records.

    Specify one or more keys of records to restore.
    To list hidden record keys, use 't show --hidden --show-keys'.

    Command aliases: 'restore', 'unhide'
    """
    now = now_timestamp()
    if not keys:
        abort("No keys provided. Specify at least one task key to remove.")

    records = get_updates()["records"]
    restored_records = []

    for r in records:
        if r["key"] in keys:
            r["ds"] = r["ds"].replace("HIDDEN ", "").strip()
            r["mt"] = now
            restored_records.append(r)

    put_records(restored_records)
    print_records((restored_records, "green"), show_keys=True)
