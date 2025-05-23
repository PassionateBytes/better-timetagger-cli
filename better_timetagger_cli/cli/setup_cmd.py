import click
from rich import print

from better_timetagger_cli.lib.config import ensure_config_file
from better_timetagger_cli.lib.misc import open_in_editor


@click.command(("setup", "configure"))  # type: ignore[call-overload]
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

    Command aliases: 'setup', 'configure'
    """

    filename = ensure_config_file()

    print(f"\nTimeTagger config file: [cyan]{filename}[/cyan]\n")

    open_in_editor(filename, editor=editor)
