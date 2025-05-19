import webbrowser

import click

from better_timetagger_cli.lib.config import load_config


@click.command()
def app() -> None:
    """
    Open the TimeTagger app in your default browser.
    """
    config = load_config()
    parts = config["api_url"].rstrip("/").split("/")
    url = "/".join(parts[:-2]) + "/app/"
    click.echo(f"Open web-app at: {url}")
    webbrowser.open(url)
