"""Tests for the load_config function."""

from textwrap import dedent

import pytest

import better_timetagger_cli.lib.config as lib


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the config cache before each test."""
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
    config_file = tmp_path / "lib.toml"
    content = dedent(f"""
        base_url = "{valid_config["base_url"]}"
        api_token = "{valid_config["api_token"]}"
        ssl_verify = {"true" if valid_config["ssl_verify"] else "false"}
        datetime_format = "{valid_config["datetime_format"]}"
        weekday_format = "{valid_config["weekday_format"]}"
    """)
    config_file.write_text(content)
    return config_file


def test_load_valid_config(monkeypatch, valid_config_file, valid_config):
    """Load valid configuration file."""
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(valid_config_file))

    config = lib.load_config()

    assert config is not None
    assert config["base_url"] == valid_config["base_url"]
    assert config["api_token"] == valid_config["api_token"]
    assert config["ssl_verify"] is True  # Converted from string
    assert config["datetime_format"] == valid_config["datetime_format"]
    assert config["weekday_format"] == valid_config["weekday_format"]


def test_caching_behavior(monkeypatch, valid_config_file):
    """Cache configuration, unless cache is disabled."""
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(valid_config_file))

    config1 = lib.load_config()
    valid_config_file.write_text(valid_config_file.read_text().replace(config1["api_token"], "new-token"))
    config2 = lib.load_config()
    assert config2["api_token"] == config1["api_token"]
    config3 = lib.load_config(cache=False)
    assert config3["api_token"] == "new-token"


def test_missing_base_url(monkeypatch, tmp_path):
    """Abort on missing base_url parameter."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text(
        dedent("""
        api_token = "test-token"
        datetime_format = "%Y-%m-%d"
        weekday_format = "%A"
    """)
    )
    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_invalid_base_url_format(monkeypatch, tmp_path):
    """Abort on invalid base_url format."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text(
        dedent("""
        base_url = "timetagger.io/timetagger/"
        api_token = "test-token"
        datetime_format = "%Y-%m-%d"
        weekday_format = "%A"
    """)
    )

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_missing_api_token(monkeypatch, tmp_path):
    """Abort on missing api_token parameter."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text(
        dedent("""
        base_url = "https://timetagger.io/timetagger/"
        datetime_format = "%Y-%m-%d"
        weekday_format = "%A"
    """)
    )

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_invalid_datetime_format(monkeypatch, tmp_path):
    """Abort on invalid datetime format string."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text(
        dedent("""
        base_url = "https://timetagger.io/timetagger/"
        api_token = "test-token"
        datetime_format = "%Q"  # %Q is an invalid code
        weekday_format = "%A"
    """)
    )

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_missing_config_file(monkeypatch, tmp_path):
    """Abort when config file doesn't exist."""
    non_existent = tmp_path / "non_existent.toml"

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(non_existent))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_invalid_toml_syntax(monkeypatch, tmp_path):
    """Abort on malformed TOML file."""
    config_file = tmp_path / "lib.toml"
    # Note: intentionally malformed - missing closing quote
    config_file.write_text(
        dedent("""
        base_url = "https://timetagger.io/timetagger/
        api_token = "test-token"
    """)
    )

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    with pytest.raises(SystemExit) as exc_info:
        lib.load_config()

    assert exc_info.value.code == 1


def test_ssl_verify_default_value(monkeypatch, tmp_path):
    """Configuation value ssl_verify defaults to True when not provided."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text(
        dedent("""
        base_url = "https://timetagger.io/timetagger/"
        api_token = "test-token"
        datetime_format = "%Y-%m-%d"
        weekday_format = "%A"
    """)
    )  # No ssl_verify specified

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    config = lib.load_config()
    assert config["ssl_verify"] is True


def test_abort_on_error_behavior(monkeypatch, tmp_path):
    """Test that abort_on_error=True raises SystemExit."""
    config_file = tmp_path / "lib.toml"
    config_file.write_text("invalid toml content [")

    monkeypatch.setattr("better_timetagger_cli.lib.config.get_config_path", lambda _: str(config_file))

    # abort by default
    with pytest.raises(SystemExit):
        lib.load_config()

    # abort on error explicitly
    with pytest.raises(SystemExit):
        lib.load_config(abort_on_error=True)

    # return none when abort is disabled
    config = lib.load_config(abort_on_error=False)
    assert config is None
