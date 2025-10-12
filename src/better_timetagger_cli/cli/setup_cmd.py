from typing import Literal

import click
from rich.box import SIMPLE
from rich.markup import escape
from rich.table import Table

from better_timetagger_cli.lib.cli import AliasedCommand
from better_timetagger_cli.lib.config import CONFIG_FILE, DEFAULT_CONFIG, get_config, get_config_filepath
from better_timetagger_cli.lib.output import abort, console, open_in_editor


@click.command(
    "setup",
    aliases=("config",),
    cls=AliasedCommand,
)
@click.option(
    "-e",
    "--editor",
    type=click.STRING,
    default=None,
    help="The name or path of the editor you want to use. By default, the configuration file will be opened in the system's default editor.",
)
@click.option(
    "-l",
    "--list",
    is_flag=False,
    flag_value="__all__",
    type=click.STRING,
    help="List all configuration options instead of opening the editor. Optionally provide a configuration key to list its value.",
)
def setup_cmd(editor: str | None, list: Literal[True] | str) -> None:
    """
    Edit the configuration file for the TimeTagger CLI.
    """

    config = get_config()
    filename = get_config_filepath(CONFIG_FILE)

    if list == "__all__":
        table = Table(show_header=False, box=SIMPLE)
        table.add_column(style="cyan", justify="right", no_wrap=True)
        table.add_column(style="magenta", overflow="fold")
        for key, default_value in DEFAULT_CONFIG.items():
            value = config.get(key, default_value)
            table.add_row(f"{key}:", escape(str(value)))
        console.print(table)
        return

    elif list:
        key = list
        if isinstance(key, str):
            value = config.get(key, DEFAULT_CONFIG.get(key, None))
        else:
            value = None
        if value is None:
            abort(f"[bold]Unknown configuration key: {key}[/bold]\nAvailable keys: {', '.join(config.keys())}")
        console.print(f"[cyan]{key}[/cyan] [magenta]{escape(str(value))}[/magenta]")
        return

    else:
        console.print(f"\nTimeTagger config file: [cyan]{filename}[/cyan]\n")
        open_in_editor(filename, editor=editor)
