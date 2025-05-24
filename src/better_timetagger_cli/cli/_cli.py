import click

from better_timetagger_cli import __version__
from better_timetagger_cli.lib.click import AliasedGroup

from .app_cmd import app_cmd
from .diagnose_cmd import diagnose_cmd
from .export_cmd import export_cmd
from .import_cmd import import_cmd
from .resume_cmd import resume_cmd
from .setup_cmd import setup_cmd
from .show_cmd import show_cmd
from .start_cmd import start_cmd
from .status_cmd import status_cmd
from .stop_cmd import stop_cmd


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
cli.add_command(app_cmd)
cli.add_command(diagnose_cmd)
cli.add_command(export_cmd)
cli.add_command(import_cmd)
cli.add_command(resume_cmd)
cli.add_command(setup_cmd)
cli.add_command(show_cmd)
cli.add_command(start_cmd)
cli.add_command(status_cmd)
cli.add_command(stop_cmd)
