from typing import Literal

import click

from better_timetagger_cli.lib.api import get_records
from better_timetagger_cli.lib.misc import abort
from better_timetagger_cli.lib.parsers import parse_start_end, tags_callback
from better_timetagger_cli.lib.records import records_to_csv


@click.command()
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=tags_callback,
)
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    help="Include records later than this time. Supports natural language.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Include records earlier than this time. Supports natural language.",
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    help="Output file. If not specified, output to stdout.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="any",
    help="Tag matching mode. Filter records that match any or all tags. Default: any.",
)
def export_cmd(
    tags: list[str],
    start: str | None,
    end: str | None,
    output: click.File | None,
    tags_match: Literal["any", "all"],
) -> None:
    """
    Export records to CSV format.

    The parameters '--start' and '--end' support natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.
    """
    start_dt, end_dt = parse_start_end(start, end)

    records = get_records(
        start_dt,
        end_dt,
        tags=tags,
        tags_match=tags_match,
        sort_by="t1",
        sort_reverse=False,
    )["records"]

    if not records:
        abort("No records found.")

    csv = records_to_csv(records)

    click.echo(csv, file=output)  # type: ignore[arg-type]
