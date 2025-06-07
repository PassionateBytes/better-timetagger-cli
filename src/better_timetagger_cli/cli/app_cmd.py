import webbrowser
from urllib.parse import urljoin

import click

from better_timetagger_cli.lib.config import load_config
from better_timetagger_cli.lib.console import console


@click.command(("app", "open"))  # type: ignore[call-overload]
def app_cmd() -> None:
    """
    Open the TimeTagger web app in the default browser.

    Command aliases: 'app', 'open'
    """

    config = load_config()
    base_url = config["base_url"].rstrip("/") + "/"
    app_url = urljoin(base_url, "app/")

    console.print(f"\nTimeTagger web app: [cyan]{app_url}[/cyan]\n")

    webbrowser.open(app_url)
