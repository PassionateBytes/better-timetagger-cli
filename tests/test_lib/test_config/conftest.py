"""Shared fixtures for lib tests."""

from textwrap import dedent

import pytest

import better_timetagger_cli.lib.config as lib


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Clear the config cache before and after each test."""
    lib._CONFIG_CACHE = None
    yield
    lib._CONFIG_CACHE = None


@pytest.fixture
def valid_config():
    """Return a valid configuration dictionary."""
    return {
        "base_url": "https://timetagger.io/timetagger/",
        "api_token": "foo-bar-test-token",
        "ssl_verify": True,
        "datetime_format": "%d-%b-%Y [bold]%H:%M[/bold]",
        "weekday_format": "%a",
    }


@pytest.fixture
def valid_config_file(valid_config, tmp_path):
    """Create a temporary valid config file."""
    config_file = tmp_path / "config.toml"
    content = dedent(f"""
        base_url = "{valid_config["base_url"]}"
        api_token = "{valid_config["api_token"]}"
        ssl_verify = {"true" if valid_config["ssl_verify"] else "false"}
        datetime_format = "{valid_config["datetime_format"]}"
        weekday_format = "{valid_config["weekday_format"]}"
    """)
    config_file.write_text(content)
    return config_file


@pytest.fixture
def mock_config_path(tmp_path):
    """Mock get_config_path to return a temporary path."""
    config_dir = tmp_path / "timetagger_cli"
    config_file = config_dir / "config.toml"

    def mock_get_config_path(filename):
        return str(config_file)

    return mock_get_config_path, config_file


@pytest.fixture
def legacy_config_file(tmp_path):
    """Create a temporary legacy config file."""
    config_file = tmp_path / "config.txt"
    content = dedent("""
        api_url = "https://example.com/timetagger/api/"
        api_token = "legacy-test-token"
        ssl_verify = false
    """)
    config_file.write_text(content)
    return config_file
