import click

from better_timetagger_cli.lib.api import get_updates, put_records
from better_timetagger_cli.lib.misc import abort, now_timestamp
from better_timetagger_cli.lib.output import print_records


@click.command(("remove", "hide"))  # type: ignore[call-overload]
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

    Specify one or more keys of records to remove from view.
    To list record keys, use 't show --show-keys'.

    Note that this command marks records as 'HIDDEN' in the TimeTagger database.
    This effectively removes them from view, but they can be restored if necessary.

    To list hidden records, use 't show --hidden'.

    Restore hidden records with 't restore'.

    Command aliases: 'remove', 'hide'
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
