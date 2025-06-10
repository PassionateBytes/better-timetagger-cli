import click

from better_timetagger_cli.lib.cli import AliasCommand
from better_timetagger_cli.lib.config import ensure_config_file
from better_timetagger_cli.lib.console import console
from better_timetagger_cli.lib.misc import open_in_editor


@click.command(
    "setup",
    aliases=("config",),
    cls=AliasCommand,
)
@click.option(
    "-e",
    "--editor",
    type=click.STRING,
    default=None,
    help="The name or path of the editor you want to use. By default, the configuration file will be opened in the system's default editor.",
)
def setup_cmd(editor: str | None) -> None:
    """
    Edit the configuration file for the TimeTagger CLI.
    """

    filename = ensure_config_file()

    console.print(f"\nTimeTagger config file: [cyan]{filename}[/cyan]\n")

    open_in_editor(filename, editor=editor)
