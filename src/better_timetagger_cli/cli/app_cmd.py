import webbrowser
from urllib.parse import urljoin

import click

from better_timetagger_cli.lib.config import get_config
from better_timetagger_cli.lib.output import console


@click.command("app")
def app_cmd() -> None:
    """
    Open the TimeTagger web app in the default browser.

    In case the application fails to open the browser, the URL will be printed to the console.
    """

    config = get_config()
    base_url = config["base_url"].rstrip("/") + "/"
    app_url = urljoin(base_url, "app/")

    console.print(f"\nTimeTagger web app: [cyan]{app_url}[/cyan]\n")

    webbrowser.open(app_url)
