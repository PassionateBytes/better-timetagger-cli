import click

from better_timetagger_cli.lib.api import get_updates, put_records
from better_timetagger_cli.lib.cli import AliasedCommand
from better_timetagger_cli.lib.output import abort, print_records
from better_timetagger_cli.lib.timestamps import now_timestamp


@click.command(
    "remove",
    aliases=("hide", "rm"),
    cls=AliasedCommand,
)
@click.argument(
    "keys",
    type=click.STRING,
    nargs=-1,
)
def remove_cmd(
    keys: list[str],
) -> None:
    """
    Hide TimeTagger records.

    Specify one or more record keys to remove.
    To list record keys, use 't show --show-keys'.

    This command marks records as 'HIDDEN' in the TimeTagger instance.
    This effectively removes them from view, but they can be restored
    later using the 't restore' command.
    """
    now = now_timestamp()
    if not keys:
        abort("No keys provided. Specify at least one task key to remove.")

    records = get_updates()["records"]
    removed_records = []

    for r in records:
        if r["key"] in keys:
            r["ds"] = f"HIDDEN {r['ds']}"
            r["mt"] = now
            removed_records.append(r)

    put_records(removed_records)
    print_records((removed_records, "red"), show_keys=True)
