import pytest


@pytest.fixture(scope="session")
def cli_runner():
    """Fixture to provide a Click runner for testing."""
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture(scope="session", autouse=True)
def default_config_file(tmp_path_factory):
    """
    Fixture to create a default configuration file for testing.
    This will be used by the CLI to ensure it has a valid config.
    """
    config_file = tmp_path_factory.mktemp("config") / "config.yaml"
    config_file.write_text("default: value\n")
    return config_file
