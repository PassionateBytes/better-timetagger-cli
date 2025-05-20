import time
from datetime import datetime, timedelta

import click

from better_timetagger_cli.lib.api import get_updates, put_records


@click.command()
@click.option(
    "-f",
    "--fix",
    is_flag=True,
    help="Fix the records that are wrong.",
)
def diagnose(fix: bool) -> None:
    """
    Load all records and perform diagnostics to detect issues.
    """

    def show_record(prefix, r):
        dt1 = datetime.fromtimestamp(r["t1"])
        dt2 = datetime.fromtimestamp(r["t2"])
        click.echo(f"{prefix}: {r['key']}, from {dt1} to {dt2}")

    # Get records and sort by t1
    records = get_updates()["records"]
    records = sorted(records, key=lambda r: r["t1"])

    # Prep
    early_date = datetime(2000, 1, 1)
    late_date = datetime.now() + timedelta(days=1)
    very_late_date = datetime.now() + timedelta(days=365 * 2)

    # Investigate records
    suspicious_records = []
    wrong_records = []

    # Add tqdm progress bar
    for r in records:
        t1, t2 = r["t1"], r["t2"]
        if t1 < 0 or t2 < 0:
            wrong_records.append(("negative timestamp", r))
        elif t1 > t2:
            wrong_records.append(("t1 larger than t2", r))
        elif datetime.fromtimestamp(r["t2"]) > very_late_date:
            wrong_records.append(("far future", r))
        elif datetime.fromtimestamp(r["t1"]) < early_date:
            suspicious_records.append(("early", r))
        elif datetime.fromtimestamp(r["t2"]) > late_date:
            suspicious_records.append(("future", r))
        elif t2 - t1 > 86400 * 2:
            suspicious_records.append(("duration over two days", r))
        elif t1 == t2 and abs(time.time() - t1) > 86400 * 2:
            ndays = round(abs(time.time() - t1) / 86400)
            suspicious_records.append((f"running for about {ndays} days", r))

    suspicious_records.sort()
    wrong_records.sort()

    # Show records
    if wrong_records:
        click.echo("Erroneous Records:")
        for prefix, r in wrong_records:
            show_record(prefix + ":", r)

    if suspicious_records:
        click.echo("Suspicious Records:")
        for prefix, r in suspicious_records:
            show_record(prefix + ":", r)

    if not wrong_records and not suspicious_records:
        click.echo("All records are valid.")

    # Fixing wrong records
    if fix:
        for prefix, r in wrong_records:
            if "t1 larger than t2" in prefix:
                r["t1"], r["t2"] = r["t2"], r["t1"]
                put_records([r])
            else:
                dt = abs(r["t1"] - r["t2"])
                if dt > 86400 * 1.2:
                    dt = 3600
                r["t1"] = int(time.time())
                r["t2"] = r["t1"] + dt
                put_records([r])
            click.echo(f"Updated {r['key']}")
