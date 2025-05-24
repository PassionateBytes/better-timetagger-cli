import pytest


@pytest.fixture(scope="session")
def cli_runner():
    """Fixture to provide a Click runner for testing."""
    from click.testing import CliRunner

    return CliRunner()
