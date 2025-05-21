import click
from rich import print

from better_timetagger_cli.lib.config import prepare_config_file
from better_timetagger_cli.lib.utils import edit_file


@click.command()
@click.option(
    "-e",
    "--editor",
    type=click.STRING,
    default=None,
    help="The name or path of the editor you want to use. By default, the configuration file will be opened in the system's default editor.",
)
def setup(editor: str | None) -> None:
    """
    Edit the configuration file for the TimeTagger CLI.
    """
    filename = prepare_config_file()
    print(f"\nTimeTagger config file: [cyan]{filename}[/cyan]")
    edit_file(filename, editor=editor)
