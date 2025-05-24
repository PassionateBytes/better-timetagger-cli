import time
from datetime import datetime, timedelta

import click
from rich.box import SIMPLE
from rich.live import Live
from rich.table import Table

from better_timetagger_cli.lib.api import get_updates, put_records
from better_timetagger_cli.lib.console import console
from better_timetagger_cli.lib.misc import abort
from better_timetagger_cli.lib.output import readable_date_time
from better_timetagger_cli.lib.types import Record


@click.command()
@click.option(
    "-f",
    "--fix",
    is_flag=True,
    help="Apply fixes to corrupt records.",
)
def diagnose_cmd(fix: bool) -> None:
    """
    Check all records for common errors and inconsistencies.

    Use the '--fix' option with caution. This will modify the records in your database!
    It is recommended to back up your database before using this option.
    """

    records = get_updates()["records"]

    if not records:
        abort("No records found.")

    error_records: list[tuple[str, Record]] = []
    warning_records: list[tuple[str, Record]] = []

    early_date = datetime(2000, 1, 1)
    late_date = datetime.now() + timedelta(days=1)
    very_late_date = datetime.now() + timedelta(days=365 * 2)

    for r in records:
        t1, t2 = r["t1"], r["t2"]

        # find errors
        if t1 < 0 or t2 < 0:
            error_records.append(
                ("negative timestamp", r),
            )
        elif t1 > t2:
            error_records.append(
                ("t1 larger than t2", r),
            )
        elif datetime.fromtimestamp(r["t2"]) > very_late_date:
            error_records.append(
                ("far future", r),
            )

        # find inconsistencies
        elif datetime.fromtimestamp(r["t1"]) < early_date:
            warning_records.append(
                ("early", r),
            )
        elif datetime.fromtimestamp(r["t2"]) > late_date:
            warning_records.append(
                ("future", r),
            )
        elif t2 - t1 > (24 * 60 * 60) * 2:
            warning_records.append(
                ("duration over two days", r),
            )
        elif t1 == t2 and abs(time.time() - t1) > (24 * 60 * 60) * 2:
            ndays = round(abs(time.time() - t1) / (24 * 60 * 60))
            warning_records.append(
                (f"running for about {ndays} days", r),
            )

    # all valid
    if not error_records and not warning_records:
        console.print(f"\n[green]All {len(records)} records are valid.[/green]\n")
        return

    # regular output
    if not fix:
        output = render_results(error_records, warning_records)
        console.print(output)
        return

    # when fixing errors, update live output as we go
    else:
        output = render_results(error_records, warning_records)
        with Live(output, console=console) as live:
            for i, (_, r) in enumerate(error_records):
                # fix t1 larger than t2
                if t1 > t2:
                    r["t1"], r["t2"] = r["t2"], r["t1"]
                    put_records([r])

                # fix negative timestamp / far future
                elif t1 < 0 or t2 < 0 or datetime.fromtimestamp(r["t2"]) > very_late_date:
                    dt = abs(r["t1"] - r["t2"])
                    if dt > (24 * 60 * 60) * 1.2:
                        dt = 60 * 60
                    r["t1"] = int(time.time())
                    r["t2"] = r["t1"] + dt
                    put_records([r])

                output = render_results(error_records, warning_records, i)
                live.update(output)


def render_results(
    error_records: list[tuple[str, Record]],
    warning_records: list[tuple[str, Record]],
    fixed_idx: int = -1,
) -> Table:
    """
    Render the results of the diagnosis.

    Args:
        error_records: List of error records.
        warning_records: List of warning records.
        fixed_idx: Index of the last fixed record.
    """

    table = Table(show_header=False, box=SIMPLE)
    table.add_column(style="red")
    table.add_column(style="magenta")
    table.add_column(style="green")

    for i, (error, r) in enumerate(error_records):
        table.add_row(
            f"{error}:",
            f"Record [bold]'{r['key']}'[/bold] from {readable_date_time(r['t1'])} to {readable_date_time(r['t2'])}",
            "...fixed!" if i <= fixed_idx else None,
        )

    for warning, r in warning_records:
        table.add_row(
            f"[yellow]{warning}:[/yellow]",
            f"Record [bold]'{r['key']}'[/bold] from {readable_date_time(r['t1'])} to {readable_date_time(r['t2'])}",
        )

    return table
