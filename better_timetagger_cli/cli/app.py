import webbrowser

import click
from rich import print

from better_timetagger_cli.lib.config import load_config


@click.command()
def app() -> None:
    """
    Open the TimeTagger app in your default browser.
    """
    config = load_config()
    parts = config["api_url"].rstrip("/").split("/")
    url = "/".join(parts[:-2]) + "/app/"
    print(f"Open web-app at: [cyan]{url}[/cyan]")
    webbrowser.open(url)
