import webbrowser

import click

from better_timetagger_cli.lib.config import load_config
from better_timetagger_cli.lib.rich_utils import console


@click.command()
def app() -> None:
    """
    Open the TimeTagger app in your default browser.
    """
    config = load_config()
    parts = config["api_url"].rstrip("/").split("/")
    url = "/".join(parts[:-2]) + "/app/"
    console.print(f"Open web-app at: [cyan]{url}[/cyan]")
    webbrowser.open(url)
