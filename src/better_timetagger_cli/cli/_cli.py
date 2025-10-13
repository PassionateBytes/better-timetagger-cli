import click

from better_timetagger_cli import __version__
from better_timetagger_cli.lib.cli import AliasedGroup

from .app_cmd import app_cmd
from .diagnose_cmd import diagnose_cmd
from .export_cmd import export_cmd
from .import_cmd import import_cmd
from .remove_cmd import remove_cmd
from .restore_cmd import restore_cmd
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

    A feature-rich and ergonomic command-line interface for TimeTagger.
    """
    pass  # pragma: no cover


# register cli commands
cli.add_command(app_cmd)
cli.add_command(diagnose_cmd)
cli.add_command(export_cmd)
cli.add_command(import_cmd)
cli.add_command(remove_cmd)
cli.add_command(restore_cmd)
cli.add_command(resume_cmd)
cli.add_command(setup_cmd)
cli.add_command(show_cmd)
cli.add_command(start_cmd)
cli.add_command(status_cmd)
cli.add_command(stop_cmd)
