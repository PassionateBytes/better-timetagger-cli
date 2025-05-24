import click
import click.testing

from better_timetagger_cli import __version__
from better_timetagger_cli.cli import cli


def test_help(cli_runner: click.testing.CliRunner) -> None:
    """Show help message"""
    for help in ("--help", "-h"):
        result = cli_runner.invoke(cli, [help])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Options:" in result.output
        assert "Commands:" in result.output
        assert "-h, --help" in result.output
        assert "--version" in result.output


def test_version(cli_runner: click.testing.CliRunner) -> None:
    """Show version"""
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "(Better) TimeTagger CLI" in result.output
    assert f"version {__version__}" in result.output
