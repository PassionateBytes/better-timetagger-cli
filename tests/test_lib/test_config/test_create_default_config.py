"""Tests for the create_default_config function."""

import os

import pytest
import tomlkit

from better_timetagger_cli.lib.config import (
    DEFAULT_CONFIG,
    LegacyConfigDict,
    create_default_config,
)


# Fixtures
@pytest.fixture
def temp_config_path(tmp_path):
    """Return a temporary config file path."""
    return str(tmp_path / "config.toml")


@pytest.fixture
def mock_stderr(monkeypatch):
    """Mock stderr.print to capture output."""
    messages = []

    def mock_print(msg, *args, **kwargs):
        messages.append(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.stderr.print", mock_print)
    return messages


@pytest.fixture
def legacy_config_dict() -> LegacyConfigDict:
    """Return a valid legacy configuration dictionary."""
    return {
        "api_url": "https://example.com/timetagger/api/v1",
        "api_token": "legacy-token-123",
        "ssl_verify": False,
    }


# Tests for creating new config without legacy
def test_create_config_with_default_values(temp_config_path, monkeypatch):
    """Create config file with default values when no legacy config exists."""
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: None)

    result = create_default_config(temp_config_path)

    assert result == temp_config_path
    assert os.path.exists(temp_config_path)

    # Verify content
    with open(temp_config_path) as f:
        config = tomlkit.load(f)

    assert config["base_url"] == DEFAULT_CONFIG["base_url"]
    assert config["api_token"] == DEFAULT_CONFIG["api_token"]
    assert config["ssl_verify"] == DEFAULT_CONFIG["ssl_verify"]
    assert config["datetime_format"] == DEFAULT_CONFIG["datetime_format"]
    assert config["weekday_format"] == DEFAULT_CONFIG["weekday_format"]
    assert config["running_records_search_window"] == DEFAULT_CONFIG["running_records_search_window"]


def test_preserve_comments_in_created_file(temp_config_path):
    """Preserve all comments from DEFAULT_CONFIG in created file."""
    create_default_config(temp_config_path)

    with open(temp_config_path) as f:
        content = f.read()

    # Check for key comment sections
    assert "# Configuration for Better-TimeTagger-CLI" in content
    assert "# =======[ TIMETAGGER URL ]=======" in content
    assert "# =======[ API TOKEN ]=======" in content
    assert "# =======[ SSL CERTIFICATE VERIFICATION ]=======" in content
    assert "# =======[ DATE/TIME FORMAT ]=======" in content
    assert "# =======[ WEEKDAY FORMAT ]=======" in content
    assert "# =======[ SEARCH OPTIMIZATION ]=======" in content


def test_create_parent_directories_if_missing(tmp_path):
    """Create parent directories when they don't exist."""
    nested_path = str(tmp_path / "deep" / "nested" / "dir" / "config.toml")

    result = create_default_config(nested_path)

    assert result == nested_path
    assert os.path.exists(nested_path)
    assert os.path.isdir(os.path.dirname(nested_path))


def test_set_file_permissions_to_0640(temp_config_path):
    """Set file permissions to 0640 for security."""
    create_default_config(temp_config_path)

    # Get file permissions
    file_stat = os.stat(temp_config_path)
    octal_perms = oct(file_stat.st_mode)[-3:]

    assert octal_perms == "640"


# Tests for legacy config migration
def test_migrate_legacy_config_values(monkeypatch, temp_config_path, legacy_config_dict, mock_stderr):
    """Migrate values from legacy config when it exists."""
    # Mock load_legacy_config to return test data
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy_config_dict)

    create_default_config(temp_config_path)

    # Verify migration message
    assert "\nMigrating legacy configuration to new format..." in mock_stderr

    # Verify migrated values
    with open(temp_config_path) as f:
        config = tomlkit.load(f)

    assert config["base_url"] == "https://example.com/timetagger/"
    assert config["api_token"] == "legacy-token-123"
    assert config["ssl_verify"] is False

    # Verify other values remain default
    assert config["datetime_format"] == DEFAULT_CONFIG["datetime_format"]
    assert config["weekday_format"] == DEFAULT_CONFIG["weekday_format"]


def test_convert_legacy_api_url_to_base_url(monkeypatch, temp_config_path):
    """Convert legacy api_url format to base_url format correctly."""
    test_cases = [
        {"api_url": "https://timetagger.io/timetagger/api/v1", "expected": "https://timetagger.io/timetagger/"},
        {"api_url": "http://localhost:8080/timetagger/api/v1", "expected": "http://localhost:8080/timetagger/"},
        {"api_url": "https://custom.domain/my-app/timetagger/api/v1", "expected": "https://custom.domain/my-app/timetagger/"},
    ]

    for case in test_cases:
        legacy = {
            "api_url": case["api_url"],
            "api_token": "token",
            "ssl_verify": True,
        }

        monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy)  # noqa: B023

        create_default_config(temp_config_path)

        with open(temp_config_path) as f:
            config = tomlkit.load(f)

        assert config["base_url"] == case["expected"]


def test_handle_legacy_config_load_failure_gracefully(monkeypatch, temp_config_path, mock_stderr):
    """Use default values when legacy config loading fails."""
    # Mock load_legacy_config to raise exception
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: (_ for _ in ()).throw(FileNotFoundError("Legacy config not found")))

    create_default_config(temp_config_path)

    # Should not print migration message
    assert not mock_stderr

    # Should create file with defaults
    with open(temp_config_path) as f:
        config = tomlkit.load(f)

    assert config["base_url"] == DEFAULT_CONFIG["base_url"]
    assert config["api_token"] == DEFAULT_CONFIG["api_token"]


# Tests for error handling
def test_abort_when_unable_to_create_directory(monkeypatch, tmp_path):
    """Abort with error message when directory creation fails."""
    read_only_path = str(tmp_path / "readonly" / "config.toml")

    # Mock makedirs to raise PermissionError
    def mock_makedirs(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("os.makedirs", mock_makedirs)

    # Mock abort
    abort_called = False
    abort_message = ""

    def mock_abort(msg):
        nonlocal abort_called, abort_message
        abort_called = True
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    with pytest.raises(SystemExit):
        create_default_config(read_only_path)

    assert abort_called
    assert "Could not create default config file: PermissionError" in abort_message
    assert "Permission denied" in abort_message


def test_abort_when_unable_to_write_file(monkeypatch, temp_config_path):
    """Abort with error message when file writing fails."""
    # Create parent directory
    os.makedirs(os.path.dirname(temp_config_path), exist_ok=True)

    # Mock open to raise IOError
    original_open = open

    def mock_open(path, mode="r"):
        if mode == "w" and path == temp_config_path:
            raise IOError("Disk full")  # noqa: UP024
        return original_open(path, mode)

    monkeypatch.setattr("builtins.open", mock_open)

    # Mock abort
    abort_message = ""

    def mock_abort(msg):
        nonlocal abort_message
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    with pytest.raises(SystemExit):
        create_default_config(temp_config_path)

    assert "Could not create default config file: OSError" in abort_message
    assert "Disk full" in abort_message


def test_abort_when_unable_to_set_permissions(monkeypatch, temp_config_path):
    """Abort with error message when chmod fails."""

    # Mock chmod to raise exception
    def mock_chmod(path, mode):
        raise OSError("Operation not permitted")

    monkeypatch.setattr("os.chmod", mock_chmod)

    # Mock abort
    abort_message = ""

    def mock_abort(msg):
        nonlocal abort_message
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    with pytest.raises(SystemExit):
        create_default_config(temp_config_path)

    assert "Could not create default config file: OSError" in abort_message
    assert "Operation not permitted" in abort_message


def test_return_filepath_on_success(temp_config_path):
    """Return the filepath when config creation succeeds."""
    result = create_default_config(temp_config_path)

    assert result == temp_config_path
    assert isinstance(result, str)


def test_handle_existing_file_overwrite(temp_config_path):
    """Overwrite existing config file without error."""
    # Create an existing file
    with open(temp_config_path, "w") as f:
        f.write("old content")

    create_default_config(temp_config_path)

    # Verify file was overwritten
    with open(temp_config_path) as f:
        content = f.read()

    assert "old content" not in content
    assert "Configuration for Better-TimeTagger-CLI" in content
