import click

from better_timetagger_cli import __version__
from better_timetagger_cli.lib.click import AliasedGroup

from .app import app
from .diagnose import diagnose
from .export import export
from .resume import resume
from .setup import setup
from .show import show
from .start import start
from .status import status
from .stop import stop


@click.group(
    cls=AliasedGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
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


# register cli commands
cli.add_command(app)
cli.add_command(diagnose)
cli.add_command(export)
cli.add_command(resume)
cli.add_command(setup)
cli.add_command(show)
cli.add_command(start)
cli.add_command(status)
cli.add_command(stop)
