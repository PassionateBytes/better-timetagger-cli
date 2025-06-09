import click
import pytest

import better_timetagger_cli.lib.click as lib


@pytest.fixture
def cli_with_aliases():
    """Create CLI with aliased commands for testing."""

    @click.group(cls=lib.AliasedGroup)
    def cli():
        """Test CLI with aliased commands."""
        pass

    @cli.command(cls=lib.AliasCommand, aliases=["s", "display", "list"])
    def show():
        """Show information."""
        click.echo("Showing data")

    @cli.command(cls=lib.AliasCommand, aliases=["del", "rm"])
    def delete():
        """Delete items."""
        click.echo("Deleting items")

    @cli.command()  # Regular command without aliases
    def create():
        """Create items."""
        click.echo("Creating items")

    return cli
