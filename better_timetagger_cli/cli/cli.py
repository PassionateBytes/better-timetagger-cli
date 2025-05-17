import click

from better_timetagger_cli import __version__
from better_timetagger_cli.lib.click_utils import AliasedGroup

from .setup import setup


@click.group(
    cls=AliasedGroup,
)
@click.version_option(
    version=__version__,
    prog_name="(Better) TimeTagger CLI",
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    (Better) TimeTagger CLI

    A command line interface for TimeTagger with a focus on functionality and usage ergonomics.
    """

    def _before_command():
        """Runs before cli command is executed."""
        pass

    def _after_command():
        """Runs after cli command is executed."""
        pass

    if ctx.invoked_subcommand is not None:
        _before_command()
        ctx.call_on_close(_after_command)


cli.add_command(setup)
