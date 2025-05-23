import webbrowser
from urllib.parse import urljoin

import click
from rich import print

from better_timetagger_cli.lib.config import load_config


@click.command(("app", "web"))  # type: ignore[call-overload]
def app() -> None:
    """
    Open the TimeTagger web app in the default browser.

    Command aliases: 'app', 'web'
    """

    config = load_config()
    base_url = config["base_url"].rstrip("/") + "/"
    app_url = urljoin(base_url, "app/")

    print(f"\nTimeTagger web app: [cyan]{app_url}[/cyan]\n")

    webbrowser.open(app_url)
