import click
import pytest

from better_timetagger_cli.lib.cli import AliasedCommand, AliasedGroup


@pytest.fixture
def cli_with_aliases():
    """Create CLI with aliased commands for testing."""

    @click.group(cls=AliasedGroup)
    def cli():
        """Test CLI with aliased commands."""
        pass

    @cli.command(cls=AliasedCommand, aliases=["s", "display", "list"])
    def show():
        """Show information."""
        click.echo("Showing data")

    @cli.command(cls=AliasedCommand, aliases=["del", "rm"])
    def delete():
        """Delete items."""
        click.echo("Deleting items")

    @cli.command()  # Regular command without aliases
    def create():
        """Create items."""
        click.echo("Creating items")

    return cli


def test_alias_command_init_with_no_aliases():
    """AliasedCommand initializes with empty aliases tuple when none provided."""
    cmd = AliasedCommand(name="test")
    assert cmd.aliases == ()


def test_alias_command_init_with_string_alias():
    """AliasedCommand converts single string alias to tuple."""
    cmd = AliasedCommand(name="test", aliases="t")
    assert cmd.aliases == ("t",)


def test_alias_command_init_with_iterable_aliases():
    """AliasedCommand converts iterable aliases to tuple."""
    cmd = AliasedCommand(name="test", aliases=["t", "tst", "testing"])
    assert cmd.aliases == ("t", "tst", "testing")


def test_alias_command_init_with_invalid_aliases():
    """AliasedCommand raises TypeError for invalid alias types."""
    with pytest.raises(TypeError):
        AliasedCommand(name="test", aliases=123)


def test_format_help_without_aliases():
    """Help output excludes aliases section when no aliases present."""
    cmd = AliasedCommand(name="test", help="A test command")
    ctx = click.Context(cmd)
    formatter = click.HelpFormatter()

    cmd.format_help(ctx, formatter)
    help_text = formatter.getvalue()

    assert "Aliases" not in help_text


def test_format_help_with_aliases():
    """Help output includes aliases section and all alias names."""
    cmd = AliasedCommand(name="test", aliases=["foo", "bar"], help="A test command")
    ctx = click.Context(cmd)
    formatter = click.HelpFormatter()

    cmd.format_help(ctx, formatter)
    help_text = formatter.getvalue()

    assert "Aliases" in help_text
    assert "test" in help_text
    assert "foo" in help_text
    assert "bar" in help_text


def test_get_command_by_name(cli_with_aliases):
    """AliasedGroup retrieves command by its original name."""
    ctx = click.Context(cli_with_aliases)
    cmd = cli_with_aliases.get_command(ctx, "show")

    assert cmd is not None
    assert cmd.name == "show"


def test_get_command_by_alias(cli_with_aliases):
    """AliasedGroup retrieves command by any of its aliases."""
    ctx = click.Context(cli_with_aliases)

    # Test all aliases for 'show' command
    for alias in ["s", "display", "list"]:
        cmd = cli_with_aliases.get_command(ctx, alias)
        assert cmd is not None
        assert cmd.name == "show"


def test_get_command_nonexistent(cli_with_aliases):
    """AliasedGroup returns None for non-existent commands."""
    ctx = click.Context(cli_with_aliases)
    cmd = cli_with_aliases.get_command(ctx, "nonexistent")

    assert cmd is None


def test_command_execution_by_name(cli_runner, cli_with_aliases):
    """Commands execute successfully by their original name."""
    result = cli_runner.invoke(cli_with_aliases, ["show"])

    assert result.exit_code == 0
    assert "Showing data" in result.output


def test_command_execution_by_alias(cli_runner, cli_with_aliases):
    """Commands execute successfully by any of their aliases."""

    # Test multiple aliases
    for alias in ["s", "display", "list"]:
        result = cli_runner.invoke(cli_with_aliases, [alias])
        assert result.exit_code == 0
        assert "Showing data" in result.output


def test_multiple_commands_with_aliases(cli_runner, cli_with_aliases):
    """Multiple commands with different aliases work independently."""

    # Test delete command aliases
    for alias in ["delete", "del", "rm"]:
        result = cli_runner.invoke(cli_with_aliases, [alias])
        assert result.exit_code == 0
        assert "Deleting items" in result.output


def test_regular_command_without_aliases(cli_runner, cli_with_aliases):
    """Regular commands without aliases continue to work normally."""
    result = cli_runner.invoke(cli_with_aliases, ["create"])

    assert result.exit_code == 0
    assert "Creating items" in result.output


def test_help_shows_aliases(cli_runner, cli_with_aliases):
    """Command help displays aliases section with all aliases."""
    result = cli_runner.invoke(cli_with_aliases, ["show", "--help"])

    assert result.exit_code == 0
    assert "Aliases" in result.output
    assert "display" in result.output
    assert "list" in result.output


def test_resolve_command_with_alias(cli_with_aliases):
    """Command resolution replaces alias with canonical name in args."""
    ctx = click.Context(cli_with_aliases)

    # Test resolving with alias
    cmd_name, cmd, args = cli_with_aliases.resolve_command(ctx, ["s"])
    assert cmd_name == "show"
    assert cmd.name == "show"
    assert args == []


def test_invalid_alias_command_execution(cli_runner, cli_with_aliases):
    """Invalid commands return error with appropriate message."""
    result = cli_runner.invoke(cli_with_aliases, ["invalid"])

    assert result.exit_code != 0
    assert "No such command" in result.output


def test_complex_cli_with_nested_commands(cli_runner):
    """Nested command groups with aliases work correctly."""

    @click.group(cls=AliasedGroup)
    def cli():
        """Main CLI."""
        pass

    @cli.group(cls=AliasedGroup, aliases=["db"])
    def database():
        """Database operations."""
        pass

    @database.command(cls=AliasedCommand, aliases=["mig", "m"])
    def migrate():
        """Run database migrations."""
        click.echo("Running migrations")

    # Test nested command with alias
    result = cli_runner.invoke(cli, ["db", "mig"])
    assert result.exit_code == 0
    assert "Running migrations" in result.output

    # Test original names
    result = cli_runner.invoke(cli, ["database", "migrate"])
    assert result.exit_code == 0
    assert "Running migrations" in result.output


def test_command_with_options_and_aliases(cli_runner):
    """Aliased commands work correctly with options and arguments."""

    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command(cls=AliasedCommand, aliases=["proc"])
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.argument("name")
    def process(verbose: bool, name: str):
        """Process something."""
        if verbose:
            click.echo(f"Verbose processing: {name}")
        else:
            click.echo(f"Processing: {name}")

    # Test alias with options
    result = cli_runner.invoke(cli, ["proc", "--verbose", "test"])
    assert result.exit_code == 0
    assert "Verbose processing: test" in result.output

    # Test original command with options
    result = cli_runner.invoke(cli, ["process", "-v", "example"])
    assert result.exit_code == 0
    assert "Verbose processing: example" in result.output


def test_empty_aliases_list():
    """Command with empty aliases list converts to empty tuple."""
    cmd = AliasedCommand(name="test", aliases=[])
    assert cmd.aliases == ()


def test_tuple_aliases():
    """Command accepts tuple aliases and preserves them correctly."""
    cmd = AliasedCommand(name="test", aliases=("a", "b", "c"))
    assert cmd.aliases == ("a", "b", "c")
