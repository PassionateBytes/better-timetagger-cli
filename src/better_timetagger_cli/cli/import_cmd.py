import sys
from typing import Literal, TextIO

import click

from better_timetagger_cli.lib.api import put_records
from better_timetagger_cli.lib.console import abort
from better_timetagger_cli.lib.csv import records_from_csv
from better_timetagger_cli.lib.output import print_records_with_summary
from better_timetagger_cli.lib.parsers import parse_start_end, tags_callback
from better_timetagger_cli.lib.records import post_process_records


@click.command("import")
@click.argument(
    "tags",
    type=click.STRING,
    nargs=-1,
    callback=tags_callback,
)
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    help="Input file. If not specified, read CSV content from stdin.",
)
@click.option(
    "-s",
    "--start",
    type=click.STRING,
    help="Include only records later than this time. Supports natural language.",
)
@click.option(
    "-e",
    "--end",
    type=click.STRING,
    help="Include only records earlier than this time. Supports natural language.",
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Only display the records that would be imported. Do not actually import them to your TimeTagger instance.",
)
@click.option(
    "-z",
    "--summary",
    "summary",
    flag_value=True,
    default=None,
    help="Show only the summary, disable table.",
)
@click.option(
    "-Z",
    "--no-summary",
    "summary",
    flag_value=False,
    default=None,
    help="Show only the table, disable summary.",
)
@click.option(
    "-v",
    "--show-keys",
    is_flag=True,
    help="List each record's unique key. Useful to when you want to remove or restore records.",
)
@click.option(
    "-x",
    "--match",
    "tags_match",
    type=click.Choice(["any", "all"]),
    default="any",
    help="Tag matching mode. Include records that match either 'any' or 'all' tags. Default: any.",
)
def import_cmd(
    tags: list[str],
    file: click.File | TextIO | None,
    start: str | None,
    end: str | None,
    dry_run: bool,
    summary: bool | None,
    show_keys: bool,
    tags_match: Literal["any", "all"],
) -> None:
    """
    Import records to CSV format.

    If no tags are provided, all tasks within the selected time frame will be included.
    Specify one or more tags to include only matching tasks.
    Tags can be entered without the leading hashtag '#'.

    The parameters '--start' and '--end' support natural language to specify date and time.
    You can use phrases like 'yesterday', 'June 11', '5 minutes ago', or '05/12 3pm'.
    """
    start_dt, end_dt = parse_start_end(start, end)
    if file is None:
        if sys.stdin.isatty():
            abort("No input. Use '--file' or pipe data to stdin.")
        file = click.get_text_stream("stdin")

    # Load records
    records = records_from_csv(file, start=start_dt, end=end_dt)  # type: ignore[arg-type]
    records = post_process_records(records, tags=tags, tags_match=tags_match)

    # In 'dry_run' mode, display the records and exit.
    if dry_run:
        print_records_with_summary(records, summary=summary, start_dt=start_dt, end_dt=end_dt, show_keys=show_keys)
        return

    # Upload records to server and update the output.
    response = put_records(records)

    record_status: dict[str, str | None] = {r["key"]: None for r in records}
    for key in response.get("accepted", ()):
        record_status[key] = "[yellow]...imported![/yellow]"
    for key in response["failed"]:
        record_status[key] = "[red]...failed![/red]"

    print_records_with_summary(records, summary=summary, start_dt=start_dt, end_dt=end_dt, show_keys=show_keys, record_status=record_status)

    if response["errors"]:
        error_msg = "\n".join(f"Import Error: {error}" for error in response["errors"])
        abort(error_msg)
