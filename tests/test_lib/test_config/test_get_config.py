"""Tests for the get_config function."""

from unittest.mock import patch

import pytest
import tomlkit

from better_timetagger_cli.lib.config import get_config


# Tests
def test_return_cached_config_when_cache_exists(monkeypatch, clear_config_cache, valid_config_dict):
    """Return cached configuration when from_cache is True and cache exists."""
    # Set the cache
    monkeypatch.setattr("better_timetagger_cli.lib.config._CONFIG_CACHE", valid_config_dict)

    # Mock file operations to ensure they're not called
    file_exists_called = False

    def mock_exists(path):  # pragma: no cover
        nonlocal file_exists_called
        file_exists_called = True
        return False

    monkeypatch.setattr("os.path.exists", mock_exists)

    # Get config with cache
    result = get_config(from_cache=True)

    assert result == valid_config_dict
    assert not file_exists_called  # Should not check file system when using cache


def test_ignore_cache_when_from_cache_false(monkeypatch, clear_config_cache, patched_config_file_path, valid_config_dict, config_dict_to_toml):
    """Ignore cached configuration when from_cache is False."""
    # Set the cache with different values
    cached_config = valid_config_dict.copy()
    cached_config["api_token"] = "cached-token"
    monkeypatch.setattr("better_timetagger_cli.lib.config._CONFIG_CACHE", cached_config)

    # Create config file with different token
    valid_config_toml = config_dict_to_toml(valid_config_dict)
    patched_config_file_path.write_text(tomlkit.dumps(valid_config_toml))

    # Get config without cache
    result = get_config(from_cache=False)

    assert result["api_token"] == "test-token-123"  # From file, not cache
    assert result != cached_config


def test_create_default_config_when_file_missing(monkeypatch, clear_config_cache, patched_config_file_path, mock_stderr, valid_config_dict):
    """Create default configuration file when no config exists."""
    # Ensure file doesn't exist
    assert not patched_config_file_path.exists()

    # Mock create_default_config to return the filepath
    create_called = False

    def mock_create_default(filepath):  # pragma: no cover
        nonlocal create_called
        create_called = True
        # Write a valid config
        toml = tomlkit.document()
        for key, value in valid_config_dict.items():
            toml[key] = value
        patched_config_file_path.write_text(tomlkit.dumps(toml))
        return filepath

    monkeypatch.setattr("better_timetagger_cli.lib.config.create_default_config", mock_create_default)

    # Get config
    result = get_config()

    assert create_called
    assert "No configuration file found" in mock_stderr[0]
    assert result == valid_config_dict


def test_load_and_validate_existing_config(monkeypatch, clear_config_cache, patched_config_file_path, valid_config_dict, config_dict_to_toml):
    """Load and validate configuration from existing file."""
    # Create config file
    valid_config_toml = config_dict_to_toml(valid_config_dict)
    patched_config_file_path.write_text(tomlkit.dumps(valid_config_toml))

    # Get config
    result = get_config()

    assert result == valid_config_dict
    assert patched_config_file_path.exists()


def test_abort_on_invalid_config_file(monkeypatch, clear_config_cache, patched_config_file_path):
    """Abort with error message when configuration file is invalid."""
    # Create invalid config file
    patched_config_file_path.write_text("invalid toml content {")

    # Mock abort to capture the error message
    abort_message = None

    def mock_abort(msg):  # pragma: no cover
        nonlocal abort_message
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    # Try to get config
    with pytest.raises(SystemExit):
        get_config()

    assert "Could not load configuration file" in abort_message
    assert "Run 't setup' to update your configuration" in abort_message


def test_abort_on_validation_error(monkeypatch, clear_config_cache, patched_config_file_path):
    """Abort with error message when configuration validation fails."""
    # Create config with missing required field
    invalid_toml = tomlkit.document()
    invalid_toml["base_url"] = "https://timetagger.io/timetagger/"
    # Missing api_token
    patched_config_file_path.write_text(tomlkit.dumps(invalid_toml))

    # Mock abort
    abort_message = None

    def mock_abort(msg):  # pragma: no cover
        nonlocal abort_message
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    # Try to get config
    with pytest.raises(SystemExit):
        get_config()

    assert "Could not load configuration file" in abort_message
    assert "ValueError" in abort_message


def test_cache_config_after_loading(monkeypatch, clear_config_cache, patched_config_file_path, valid_config_dict, config_dict_to_toml):
    """Cache configuration after successfully loading from file."""
    # Create config file
    valid_config_toml = config_dict_to_toml(valid_config_dict)
    patched_config_file_path.write_text(tomlkit.dumps(valid_config_toml))

    # Import the module to access _CONFIG_CACHE directly
    from better_timetagger_cli.lib import config

    # Verify cache is initially None
    assert config._CONFIG_CACHE is None

    # Get config
    result = get_config()

    # Verify cache was set
    assert config._CONFIG_CACHE is not None
    assert config._CONFIG_CACHE == valid_config_dict

    # Verify subsequent calls use cache by tracking file reads with context manager
    file_read_count = 0
    original_open = open

    def count_file_reads(filepath, *args, **kwargs):  # pragma: no cover
        nonlocal file_read_count
        if str(filepath) == str(patched_config_file_path):
            file_read_count += 1
        return original_open(filepath, *args, **kwargs)

    with patch("builtins.open", side_effect=count_file_reads):
        # Get config again
        result2 = get_config()

    assert result2 == result
    assert file_read_count == 0  # Should not read file again


def test_handle_file_permission_error(monkeypatch, clear_config_cache, patched_config_file_path):
    """Abort gracefully when unable to read configuration file."""
    # Create config file
    patched_config_file_path.write_text("dummy content")

    # Mock abort
    abort_message = None

    def mock_abort(msg):  # pragma: no cover
        nonlocal abort_message
        abort_message = msg
        raise SystemExit(msg)

    monkeypatch.setattr("better_timetagger_cli.lib.config.abort", mock_abort)

    # Mock open to raise PermissionError only for our specific config file using context manager
    original_open = open

    def selective_mock_open(filepath, *args, **kwargs):  # pragma: no cover
        if str(filepath) == str(patched_config_file_path):
            raise PermissionError("Permission denied")
        return original_open(filepath, *args, **kwargs)

    with patch("builtins.open", side_effect=selective_mock_open):
        # Try to get config
        with pytest.raises(SystemExit):
            get_config()

    assert "Could not load configuration file" in abort_message
    assert "PermissionError" in abort_message
    assert "Permission denied" in abort_message


def test_preserve_optional_config_values(monkeypatch, clear_config_cache, patched_config_file_path):
    """Preserve optional configuration values when present in file."""
    # Create config with custom optional values
    config_toml = tomlkit.document()
    config_toml["base_url"] = "https://custom.domain/timetagger/"
    config_toml["api_token"] = "custom-token"
    config_toml["ssl_verify"] = "/path/to/cert"  # String instead of bool
    config_toml["datetime_format"] = "%Y-%m-%d %H:%M"
    config_toml["weekday_format"] = "%A"  # Full weekday
    config_toml["running_records_search_window"] = -1  # Search all

    patched_config_file_path.write_text(tomlkit.dumps(config_toml))

    # Get config
    result = get_config()

    assert result["ssl_verify"] == "/path/to/cert"
    assert result["datetime_format"] == "%Y-%m-%d %H:%M"
    assert result["weekday_format"] == "%A"
    assert result["running_records_search_window"] == -1
