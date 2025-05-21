import time
from datetime import datetime, timedelta

import click
from rich import print
from rich.box import SIMPLE
from rich.live import Live
from rich.table import Table

from better_timetagger_cli.lib.api import get_updates, put_records
from better_timetagger_cli.lib.utils import readable_time


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
    early_date = datetime(2000, 1, 1)
    late_date = datetime.now() + timedelta(days=1)
    very_late_date = datetime.now() + timedelta(days=365 * 2)

    records = get_updates()["records"]
    suspicious_records = []
    wrong_records = []

    for r in reversed(records):
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

    if not wrong_records and not suspicious_records:
        print("[green]All records are valid.")
        return

    def render_table(fixed_idx: int = -1) -> Table:
        table = Table(show_header=False, box=SIMPLE)
        table.add_column(justify="left", style="red")
        table.add_column(justify="left", style="magenta")
        table.add_column(justify="left", style="green")
        for i, (prefix, r) in enumerate(wrong_records):
            if i <= fixed_idx:
                table.add_row(f"{prefix}:", f"Record '{r['key']}' from {readable_time(r['t1'])} to {readable_time(r['t2'])}", "...fixed!")
            else:
                table.add_row(f"{prefix}:", f"Record '{r['key']}' from {readable_time(r['t1'])} to {readable_time(r['t2'])}")
        for prefix, r in suspicious_records:
            table.add_row(f"[yellow]{prefix}:", f"Record '{r['key']}' from {readable_time(r['t1'])} to {readable_time(r['t2'])}")
        return table

    if fix:
        with Live() as live:
            for i, (_, r) in enumerate(wrong_records):
                if t1 > t2:
                    r["t1"], r["t2"] = r["t2"], r["t1"]
                    put_records([r])
                elif (t1 < 0 or t2 < 0) or (datetime.fromtimestamp(r["t2"]) > very_late_date):
                    dt = abs(r["t1"] - r["t2"])
                    if dt > 86400 * 1.2:
                        dt = 3600
                    r["t1"] = int(time.time())
                    r["t2"] = r["t1"] + dt
                    put_records([r])
                live.update(render_table(i))

    else:
        print(render_table())
