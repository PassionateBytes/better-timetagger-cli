"""Shared test fixtures for all test modules."""

import pytest
import tomlkit

from better_timetagger_cli.lib.config import (
    CONFIG_FILE,
    ConfigDict,
    LegacyConfigDict,
)


@pytest.fixture
def mock_stderr(monkeypatch):
    """Mock stderr.print to capture output."""
    messages = []

    def mock_print(msg, *args, **kwargs):
        messages.append(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.stderr.print", mock_print)
    return messages


@pytest.fixture
def clear_config_cache(monkeypatch):
    """Clear the configuration cache before each test."""
    monkeypatch.setattr("better_timetagger_cli.lib.config._CONFIG_CACHE", None)


@pytest.fixture
def config_file_path(tmp_path):
    """Create a temporary config file path."""
    return tmp_path / CONFIG_FILE


@pytest.fixture
def patched_config_file_path(monkeypatch, tmp_path):
    """
    Create a temporary config file path and patch get_config_filepath to use it.

    This is useful for tests that need to mock the config file location.
    """
    config_path = tmp_path / CONFIG_FILE
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_filepath", lambda _: str(config_path))
    return config_path


@pytest.fixture
def valid_config_dict():
    """Return a valid configuration dictionary."""
    return ConfigDict(
        base_url="https://timetagger.io/timetagger/",
        api_token="test-token-123",
        ssl_verify=True,
        datetime_format="%d-%b-%Y [bold]%H:%M[/bold]",
        weekday_format="%a",
        running_records_search_window=4,
    )


@pytest.fixture
def custom_config_dict():
    """Return a custom configuration dictionary with non-default values."""
    return ConfigDict(
        base_url="https://custom.domain/timetagger/",
        api_token="custom-token-456",
        ssl_verify="/path/to/cert.pem",
        datetime_format="%Y-%m-%d %H:%M:%S",
        weekday_format="%A",
        running_records_search_window=-1,
    )


@pytest.fixture
def legacy_config_dict() -> LegacyConfigDict:
    """Return a valid legacy configuration dictionary."""
    return {
        "api_url": "https://example.com/timetagger/api/v1",
        "api_token": "legacy-token-123",
        "ssl_verify": False,
    }


@pytest.fixture
def minimal_valid_toml():
    """Return a minimal valid TOML document with only required fields."""
    toml = tomlkit.document()
    toml["base_url"] = "https://timetagger.io/timetagger/"
    toml["api_token"] = "test-token-123"
    return toml


@pytest.fixture
def full_valid_toml():
    """Return a complete valid TOML document with all fields."""
    toml = tomlkit.document()
    toml["base_url"] = "https://custom.domain/timetagger/"
    toml["api_token"] = "custom-token-456"
    toml["ssl_verify"] = "/path/to/cert.pem"
    toml["datetime_format"] = "%Y-%m-%d %H:%M:%S"
    toml["weekday_format"] = "%A"
    toml["running_records_search_window"] = -1
    return toml


@pytest.fixture
def config_dict_to_toml():
    """Convert a ConfigDict to a TOML document."""

    def _convert(config_dict: ConfigDict):
        toml = tomlkit.document()
        for key, value in config_dict.items():
            toml[key] = value
        return toml

    return _convert
