"""Tests for the create_default_config function."""

import stat
from unittest.mock import patch

import pytest
import toml

import better_timetagger_cli.lib.config as lib


def test_create_default_config_with_default_values(monkeypatch, mock_config_path):
    """Create default config file with factory default values."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)

    # Mock load_legacy_config to return None (no legacy config)
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: None)

    result_path = lib.create_default_config()

    assert result_path == str(config_file)
    assert config_file.exists()

    # Verify file permissions (readable by owner and group, not world)
    file_stat = config_file.stat()
    assert stat.filemode(file_stat.st_mode) == "-rw-r-----"

    # Verify config content
    content = config_file.read_text()

    config_data = toml.loads(content)
    assert config_data["base_url"] == lib.DEFAULT_CONFIG_DATA["base_url"]
    assert config_data["api_token"] == lib.DEFAULT_CONFIG_DATA["api_token"]
    assert config_data["ssl_verify"] is (True if lib.DEFAULT_CONFIG_DATA["ssl_verify"] == "true" else False)
    assert config_data["datetime_format"] == lib.DEFAULT_CONFIG_DATA["datetime_format"]
    assert config_data["weekday_format"] == lib.DEFAULT_CONFIG_DATA["weekday_format"]


def test_create_default_config_with_legacy_values(monkeypatch, mock_config_path, legacy_config_file):
    """Create default config file using values from legacy config."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)

    # Mock load_legacy_config to return legacy values
    legacy_config = {"api_url": "https://example.com/timetagger/api/", "api_token": "legacy-test-token", "ssl_verify": False}
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy_config)

    result_path = lib.create_default_config()

    assert result_path == str(config_file)
    assert config_file.exists()

    # Verify config content uses legacy values
    content = config_file.read_text()
    config_data = toml.loads(content)
    assert config_data["base_url"] == "https://example.com/"  # URL path adjusted
    assert config_data["api_token"] == "legacy-test-token"
    assert config_data["ssl_verify"] is False
    # Other values should remain default
    assert config_data["datetime_format"] == lib.DEFAULT_CONFIG_DATA["datetime_format"]
    assert config_data["weekday_format"] == lib.DEFAULT_CONFIG_DATA["weekday_format"]


def test_create_default_config_creates_directory(monkeypatch, tmp_path):
    """Create config directory if it doesn't exist."""
    config_dir = tmp_path / "nested" / "timetagger_cli"
    config_file = config_dir / "config.toml"

    def mock_get_config_path(filename):
        return str(config_file)

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: None)

    # Ensure directory doesn't exist initially
    assert not config_dir.exists()

    result_path = lib.create_default_config()

    assert result_path == str(config_file)
    assert config_dir.exists()
    assert config_file.exists()


def test_create_default_config_handles_legacy_config_error(monkeypatch, mock_config_path):
    """Fall back to default values when legacy config loading fails."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)

    # Mock load_legacy_config to raise an exception
    def failing_legacy_load():
        raise Exception("Legacy config error")

    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", failing_legacy_load)

    result_path = lib.create_default_config()

    assert result_path == str(config_file)
    assert config_file.exists()

    # Verify config uses default values
    content = config_file.read_text()

    config_data = toml.loads(content)
    assert config_data["base_url"] == lib.DEFAULT_CONFIG_DATA["base_url"]
    assert config_data["api_token"] == lib.DEFAULT_CONFIG_DATA["api_token"]


def test_create_default_config_file_write_error(monkeypatch, tmp_path):
    """Abort when unable to write config file."""
    # Create a directory where the config file should be (causing write error)
    config_path = tmp_path / "config.toml"
    config_path.mkdir()

    def mock_get_config_path(filename):
        return str(config_path)

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        lib.create_default_config()

    assert exc_info.value.code == 1


def test_create_default_config_permission_error(monkeypatch, mock_config_path):
    """Abort when unable to set file permissions."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: None)

    # Mock os.chmod to raise an exception
    def failing_chmod(path, mode):
        raise OSError("Permission denied")

    with patch("os.chmod", failing_chmod):
        with pytest.raises(SystemExit) as exc_info:
            lib.create_default_config()

        assert exc_info.value.code == 1


def test_create_default_config_legacy_url_parsing(monkeypatch, mock_config_path):
    """Parse legacy API URL correctly to extract base URL."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)

    # Test various legacy URL formats
    test_cases = [
        {"legacy_url": "https://example.com/timetagger/api/", "expected_base": "https://example.com/"},
        {"legacy_url": "http://localhost:8080/timetagger/api/", "expected_base": "http://localhost:8080/"},
        {"legacy_url": "https://subdomain.example.com/path/timetagger/api/", "expected_base": "https://subdomain.example.com/path/"},
    ]

    for test_case in test_cases:
        # Reset config file for each test
        if config_file.exists():
            config_file.unlink()

        legacy_config = {"api_url": test_case["legacy_url"], "api_token": "test-token", "ssl_verify": True}
        monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy_config)  # noqa: B023

        lib.create_default_config()

        content = config_file.read_text()

        config_data = toml.loads(content)
        assert config_data["base_url"] == test_case["expected_base"]


def test_create_default_config_ssl_verify_conversion(monkeypatch, mock_config_path):
    """Convert legacy ssl_verify boolean to string format."""
    mock_get_config_path, config_file = mock_config_path
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", mock_get_config_path)

    # Test ssl_verify = True
    legacy_config_true = {"api_url": "https://example.com/timetagger/api/", "api_token": "test-token", "ssl_verify": True}
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy_config_true)

    lib.create_default_config()

    content = config_file.read_text()

    config_data = toml.loads(content)
    assert config_data["ssl_verify"] is True

    # Reset and test ssl_verify = False
    config_file.unlink()

    legacy_config_false = {"api_url": "https://example.com/timetagger/api/", "api_token": "test-token", "ssl_verify": False}
    monkeypatch.setattr("better_timetagger_cli.lib.config.load_legacy_config", lambda: legacy_config_false)

    lib.create_default_config()

    content = config_file.read_text()

    config_data = toml.loads(content)
    assert config_data["ssl_verify"] is False
