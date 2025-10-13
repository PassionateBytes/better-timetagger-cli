"""Tests for the validate_config function."""

import pytest
import tomlkit

from better_timetagger_cli.lib.config import DEFAULT_CONFIG, validate_config


# Tests for successful validation
def test_validate_minimal_config_applies_defaults(minimal_valid_toml):
    """Apply default values for optional fields when not provided."""
    result = validate_config(minimal_valid_toml)

    assert result["base_url"] == "https://timetagger.io/timetagger/"
    assert result["api_token"] == "test-token-123"
    assert result["ssl_verify"] == DEFAULT_CONFIG["ssl_verify"]
    assert result["datetime_format"] == DEFAULT_CONFIG["datetime_format"]
    assert result["weekday_format"] == DEFAULT_CONFIG["weekday_format"]
    assert result["running_records_search_window"] == DEFAULT_CONFIG["running_records_search_window"]


def test_validate_full_config_preserves_all_values(full_valid_toml):
    """Preserve all provided values without applying defaults."""
    result = validate_config(full_valid_toml)

    assert result["base_url"] == "https://custom.domain/timetagger/"
    assert result["api_token"] == "custom-token-456"
    assert result["ssl_verify"] == "/path/to/cert.pem"
    assert result["datetime_format"] == "%Y-%m-%d %H:%M:%S"
    assert result["weekday_format"] == "%A"
    assert result["running_records_search_window"] == -1


def test_strip_whitespace_from_format_strings(minimal_valid_toml):
    """Strip whitespace from datetime and weekday format strings."""
    minimal_valid_toml["datetime_format"] = "  %Y-%m-%d  "
    minimal_valid_toml["weekday_format"] = "\t%a\n"

    result = validate_config(minimal_valid_toml)

    assert result["datetime_format"] == "%Y-%m-%d"
    assert result["weekday_format"] == "%a"


def test_accept_http_and_https_urls(minimal_valid_toml):
    """Accept both HTTP and HTTPS URLs for base_url."""
    # Test HTTPS
    minimal_valid_toml["base_url"] = "https://example.com/timetagger/"
    result = validate_config(minimal_valid_toml)
    assert result["base_url"] == "https://example.com/timetagger/"

    # Test HTTP
    minimal_valid_toml["base_url"] = "http://localhost:8080/timetagger/"
    result = validate_config(minimal_valid_toml)
    assert result["base_url"] == "http://localhost:8080/timetagger/"


def test_accept_boolean_ssl_verify():
    """Accept boolean values for ssl_verify."""
    toml = tomlkit.document()
    toml["base_url"] = "https://example.com/"
    toml["api_token"] = "token"

    # Test True
    toml["ssl_verify"] = True
    result = validate_config(toml)
    assert result["ssl_verify"] is True

    # Test False
    toml["ssl_verify"] = False
    result = validate_config(toml)
    assert result["ssl_verify"] is False


def test_accept_valid_search_window_values(minimal_valid_toml):
    """Accept positive integers and -1 for running_records_search_window."""
    # Test positive values
    for value in [1, 10, 100]:
        minimal_valid_toml["running_records_search_window"] = value
        result = validate_config(minimal_valid_toml)
        assert result["running_records_search_window"] == value

    # Test -1
    minimal_valid_toml["running_records_search_window"] = -1
    result = validate_config(minimal_valid_toml)
    assert result["running_records_search_window"] == -1


# Tests for missing required fields
def test_raise_error_when_base_url_missing():
    """Raise ValueError when base_url is not set."""
    toml = tomlkit.document()
    toml["api_token"] = "token"

    with pytest.raises(ValueError, match="Parameter 'base_url' not set"):
        validate_config(toml)


def test_raise_error_when_base_url_empty():
    """Raise ValueError when base_url is empty string."""
    toml = tomlkit.document()
    toml["base_url"] = ""
    toml["api_token"] = "token"

    with pytest.raises(ValueError, match="Parameter 'base_url' not set"):
        validate_config(toml)


def test_raise_error_when_api_token_missing():
    """Raise ValueError when api_token is not set."""
    toml = tomlkit.document()
    toml["base_url"] = "https://example.com/"

    with pytest.raises(ValueError, match="Parameter 'api_token' not set"):
        validate_config(toml)


def test_raise_error_when_api_token_empty():
    """Raise ValueError when api_token is empty string."""
    toml = tomlkit.document()
    toml["base_url"] = "https://example.com/"
    toml["api_token"] = ""

    with pytest.raises(ValueError, match="Parameter 'api_token' not set"):
        validate_config(toml)


# Tests for invalid types
def test_raise_error_when_base_url_not_string(minimal_valid_toml):
    """Raise ValueError when base_url is not a string."""
    minimal_valid_toml["base_url"] = 123

    with pytest.raises(ValueError, match="Parameter 'base_url' must be a string"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_api_token_not_string(minimal_valid_toml):
    """Raise ValueError when api_token is not a string."""
    minimal_valid_toml["api_token"] = ["token", "list"]

    with pytest.raises(ValueError, match="Parameter 'api_token' must be a string"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_ssl_verify_invalid_type(minimal_valid_toml):
    """Raise ValueError when ssl_verify is not bool or string."""
    minimal_valid_toml["ssl_verify"] = 123

    with pytest.raises(ValueError, match="Parameter 'ssl_verify' must be a boolean or a string"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_datetime_format_not_string(minimal_valid_toml):
    """Raise ValueError when datetime_format is not a string."""
    minimal_valid_toml["datetime_format"] = 123

    with pytest.raises(ValueError, match="Parameter 'datetime_format' must be a string"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_weekday_format_not_string(minimal_valid_toml):
    """Raise ValueError when weekday_format is not a string."""
    minimal_valid_toml["weekday_format"] = True

    with pytest.raises(ValueError, match="Parameter 'weekday_format' must be a string"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_search_window_not_integer(minimal_valid_toml):
    """Raise ValueError when running_records_search_window is not an integer."""
    minimal_valid_toml["running_records_search_window"] = 3.14

    with pytest.raises(ValueError, match="Parameter 'running_records_search_window' must be an integer"):
        validate_config(minimal_valid_toml)


# Tests for invalid values
def test_raise_error_when_base_url_invalid_protocol(minimal_valid_toml):
    """Raise ValueError when base_url doesn't start with http:// or https://."""
    invalid_urls = [
        "ftp://example.com/",
        "example.com/timetagger/",
        "//example.com/timetagger/",
        "file:///path/to/file",
    ]

    for url in invalid_urls:
        minimal_valid_toml["base_url"] = url
        with pytest.raises(ValueError, match="Parameter 'base_url' must start with 'http://' or 'https://'"):
            validate_config(minimal_valid_toml)


def test_raise_error_when_datetime_format_invalid(minimal_valid_toml):
    """Raise ValueError when datetime_format has invalid strftime codes."""
    minimal_valid_toml["datetime_format"] = "%Y-%m-%d %Q"  # %Q is invalid

    with pytest.raises(ValueError, match="Parameter 'datetime_format' is invalid"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_weekday_format_invalid(minimal_valid_toml):
    """Raise ValueError when weekday_format has invalid strftime codes."""
    minimal_valid_toml["weekday_format"] = "%X%Z%Q"  # %Q is invalid

    with pytest.raises(ValueError, match="Parameter 'weekday_format' is invalid"):
        validate_config(minimal_valid_toml)


def test_raise_error_when_search_window_invalid_range(minimal_valid_toml):
    """Raise ValueError when running_records_search_window is not >0 or -1."""
    invalid_values = [0, -2, -10, -100]

    for value in invalid_values:
        minimal_valid_toml["running_records_search_window"] = value
        with pytest.raises(ValueError, match="Parameter 'running_records_search_window' must be larger than 0 or exacly -1"):
            validate_config(minimal_valid_toml)


def test_raise_error_when_search_window_invalid_none(minimal_valid_toml):
    """Raise ValueError when running_records_search_window is not a valid type or value."""
    minimal_valid_toml["running_records_search_window"] = ""

    config = validate_config(minimal_valid_toml)
    assert config["running_records_search_window"] == DEFAULT_CONFIG["running_records_search_window"]


# Tests for empty optional fields
def test_use_default_when_datetime_format_empty(minimal_valid_toml):
    """Use default value when datetime_format is empty string."""
    minimal_valid_toml["datetime_format"] = ""

    result = validate_config(minimal_valid_toml)

    assert result["datetime_format"] == DEFAULT_CONFIG["datetime_format"]


def test_use_default_when_weekday_format_empty(minimal_valid_toml):
    """Use default value when weekday_format is empty string."""
    minimal_valid_toml["weekday_format"] = ""

    result = validate_config(minimal_valid_toml)

    assert result["weekday_format"] == DEFAULT_CONFIG["weekday_format"]


def test_use_default_when_search_window_empty(minimal_valid_toml):
    """Use default value when running_records_search_window is empty."""
    result = validate_config(minimal_valid_toml)

    assert result["running_records_search_window"] == DEFAULT_CONFIG["running_records_search_window"]


# Test for type guard
def test_raise_error_when_config_structure_invalid(monkeypatch):
    """Raise ValueError when config doesn't match ConfigDict structure."""
    # Mock is_config_dict to return False
    monkeypatch.setattr("better_timetagger_cli.lib.config.is_config_dict", lambda _: False)

    toml = tomlkit.document()
    toml["base_url"] = "https://example.com/"
    toml["api_token"] = "token"

    with pytest.raises(ValueError, match="Invalid configuration structure. Expected a ConfigDict"):
        validate_config(toml)
