"""
### Configuration Management

Utility functions to interact with configuration files for the application.
"""

# Developer's Note:
#   This module heavily relies on `tomlkit`, because other than most
#   toml serialization libraries it preserves comments and layout of
#   the in the toml file. This allows us to define the default config
#   file content along with explanatory comments here, parse and modify
#   it as a dictionary for programmatic use, then dump it to the
#   filesystem with all its comments intact. We can also modify the
#   user's configuration file in place, without impacting their config
#   file layout.

import os
from datetime import datetime
from pathlib import Path
from typing import TypeGuard, cast
from urllib.parse import urlparse, urlunparse

import tomlkit
from platformdirs import user_config_dir
from tomlkit import TOMLDocument

from better_timetagger_cli import __author__

from .output import abort, stderr
from .types import ConfigDict, LegacyConfigDict

CONFIG_FILE = "config.toml"
LEGACY_CONFIG_FILE = "config.txt"

DEFAULT_CONFIG = tomlkit.loads("""\
# Configuration for Better-TimeTagger-CLI
# Clear or remove this file to reset to factory defaults.


# =======[ TIMETAGGER URL ]=======

# This is the base URL of the TimeTagger API for your instance.

base_url = "https://timetagger.io/timetagger/"
# base_url = "http://localhost:8080/timetagger/"  # -> local instance
# base_url = "https://your.domain.net/timetagger/"  # -> self-hosted instance


# =======[ API TOKEN ]=======

# You find your api token in the TimeTagger web application, on the account page.

api_token = "<your api token>"


# =======[ SSL CERTIFICATE VERIFICATION ]=======

# If you're self-hosting, you might need to set your own self-signed certificate or disable the verification of SSL certificate.
# Disabling the certificate verification is a potentially risky action that might expose your application to attacks.
# You can set the path to a self signed certificate for verification and validation.
# For more information, visit: https://letsencrypt.org/docs/certificates-for-localhost/

ssl_verify = true
# ssl_verify = false  # -> disables SSL verification
# ssl_verify = "path/to/certificate"  # -> path to self-signed certificate


# =======[ DATE/TIME FORMAT ]=======

# This format-string is used to render dates and times in the command line interface.
# For more information, visit: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

datetime_format = "%d-%b-%Y [bold]%H:%M[/bold]"
# datetime_format = "%m/%d/%Y [bold]%I:%M %P[/bold]"  # -> US-American date with 12hr am/pm time
# datetime_format = "%d.%m.%Y [bold]%H:%M[/bold]"  # -> European date with 24hr time
# datetime_format = "%Y-%m-%dT%H:%M:%S"  # -> ISO 8601 format


# =======[ WEEKDAY FORMAT ]=======

# This format-string is used to render weekdays in the command line interface.
# For more information, visit: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

weekday_format = "%a"
# weekday_format = "%A"  # -> full weekday name


# =======[ SEARCH OPTIMIZATION ]=======

# This parameter defines how the CLI will find actively running records in the database.
# If set to -1, the CLI will search all existing records to find running ones. This is the most accurate method,
# and makes it possible to find very long running tasks that might have been started weeks ago.
# If set to a value above 0, the CLI will only search for running records in as many weeks recent weeks.
# Setting this to -1 will result in slower performance, especially when there are a lot of records in the database.
# If you are dealing with very long running tasks however, you might want tweak this value or set it to -1.

running_records_search_window = 4
# running_records_search_window = -1  # -> search all records (may impact performance)
""")


_CONFIG_CACHE: ConfigDict | None = None


def get_config(from_cache: bool = True) -> ConfigDict:
    """
    Load, validate and if necessary create the configuration file.

    Configuration is cached by default, for subsequent calls to this function.

    Args:
        from_cache: Whether to return results from the cache if possible. Default True.

    Returns:
        A valid configuration dictionary.
    """
    global _CONFIG_CACHE
    if from_cache and _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    # create default configuration if none exists
    filepath = get_config_filepath(CONFIG_FILE)
    if not os.path.exists(filepath):
        stderr.print("\nNo configuration file found, initializing configuration...", style="yellow")
        filepath = create_default_config(filepath)

    # load configuration file
    try:
        with open(filepath) as file:
            toml = tomlkit.load(file)
        config = validate_config(toml)
    except Exception as e:
        abort(f"Could not load configuration file: {e.__class__.__name__}\n[dim]{e}[/dim]\n\nRun 't setup' to update your configuration.")

    _CONFIG_CACHE = config
    return config


def validate_config(config: TOMLDocument) -> ConfigDict:
    """
    Validate the configuration dictionary.

    Args:
        config: The configuration toml document to validate.

    Raises:
        ValueError: If any required parameter is missing or invalid.
    """
    base_url = config.get("base_url", "")
    if not base_url:
        raise ValueError("Parameter 'base_url' not set.")
    if not isinstance(base_url, str):
        raise ValueError("Parameter 'base_url' must be a string.")
    if not base_url.startswith(("http://", "https://")):
        raise ValueError("Parameter 'base_url' must start with 'http://' or 'https://'.")

    api_token = config.get("api_token", "")
    if not api_token:
        raise ValueError("Parameter 'api_token' not set.")
    if not isinstance(api_token, str):
        raise ValueError("Parameter 'api_token' must be a string.")

    verify_ssl = config.get("ssl_verify", DEFAULT_CONFIG["ssl_verify"])
    if not isinstance(verify_ssl, bool | str):
        raise ValueError("Parameter 'ssl_verify' must be a boolean or a string.")
    config["ssl_verify"] = verify_ssl

    datetime_format = config.get("datetime_format", DEFAULT_CONFIG["datetime_format"])
    if not datetime_format:
        datetime_format = DEFAULT_CONFIG["datetime_format"]
    if not isinstance(datetime_format, str):
        raise ValueError("Parameter 'datetime_format' must be a string.")
    if not validate_strftime_format(datetime_format):
        raise ValueError("Parameter 'datetime_format' is invalid.")
    config["datetime_format"] = datetime_format.strip()

    weekday_format = config.get("weekday_format", DEFAULT_CONFIG["weekday_format"])
    if not weekday_format:
        weekday_format = DEFAULT_CONFIG["weekday_format"]
    if not isinstance(weekday_format, str):
        raise ValueError("Parameter 'weekday_format' must be a string.")
    if not validate_strftime_format(weekday_format):
        raise ValueError("Parameter 'weekday_format' is invalid.")
    config["weekday_format"] = weekday_format.strip()

    running_records_search_window = config.get("running_records_search_window", DEFAULT_CONFIG["running_records_search_window"])
    if not running_records_search_window and running_records_search_window != 0:
        running_records_search_window = DEFAULT_CONFIG["running_records_search_window"]
    if not isinstance(running_records_search_window, int):
        raise ValueError("Parameter 'running_records_search_window' must be an integer.")
    if not (running_records_search_window > 0 or running_records_search_window == -1):
        raise ValueError("Parameter 'running_records_search_window' must be larger than 0 or exacly -1.")
    config["running_records_search_window"] = running_records_search_window

    # type-guard
    if not is_config_dict(config):
        raise ValueError("Invalid configuration structure. Expected a ConfigDict.")

    return config


def is_config_dict(toml: TOMLDocument) -> TypeGuard[ConfigDict]:
    """
    Validate that the object has all required keys of the ConfigDict.
    """
    return all(key in toml for key in ConfigDict.__required_keys__)


def validate_strftime_format(format_string: str) -> bool:
    """
    Validate a strftime format string.

    Args:
        format_string: The format string to validate.

    Returns:
        True if the format string is valid, False otherwise.
    """
    try:
        now = datetime.now().strftime(format_string)
        if "%" in now:
            raise ValueError("Format string contains unrecognized format codes.")
        return True
    except (ValueError, TypeError):
        return False


def get_config_filepath(config_file: str) -> str:
    """
    Get the path to the config file.

    Args:
        config_file: The name of the config file.

    Returns:
        The path to the config file.
    """
    return os.path.join(
        user_config_dir(appname="timetagger_cli", appauthor=__author__, roaming=True),
        config_file,
    )


def create_default_config(filepath: str = get_config_filepath(CONFIG_FILE)) -> str:
    """
    Create a new configuration file.

    Grab default values from the legacy config file if possible.
    Otherwise, just use the default values.

    Returns:
        The path to the configuration file.
    """
    new_config = DEFAULT_CONFIG.copy()

    # attempt loading legacy config values
    try:
        legacy_config = load_legacy_config()
        url = urlparse(legacy_config["api_url"])
        url_path = Path(url.path).parents[1]
        url = url._replace(path=str(url_path))
        base_url = urlunparse(url).rstrip("/") + "/"

        stderr.print("\nMigrating legacy configuration to new format...", style="yellow")
        new_config["base_url"] = base_url
        new_config["api_token"] = legacy_config["api_token"]
        new_config["ssl_verify"] = legacy_config["ssl_verify"]
    except Exception:
        pass

    # write config file
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as file:
            tomlkit.dump(new_config, file)
        os.chmod(filepath, 0o640)
        return filepath

    except Exception as e:
        abort(f"Could not create default config file: {e.__class__.__name__}\n[dim]{e}[/dim]")


def load_legacy_config(filepath: str = get_config_filepath(LEGACY_CONFIG_FILE)) -> LegacyConfigDict:
    """
    Load and validate the legacy config from the filesystem.

    Args:
        filepath: The path to the legacy config file.

    Returns:
        The loaded configuration as a dictionary. None if the config is invalid or not reachable.
    """
    with open(filepath) as file:
        config = tomlkit.load(file)

    # validate required keys
    api_url = config.get("api_url")
    api_token = config.get("api_token")
    if not api_url or not isinstance(api_url, str) or not api_url.startswith(("http://", "https://")) or not api_token or not isinstance(api_token, str):
        raise ValueError("Invalid configuration values.")

    # validate optional keys
    config["ssl_verify"] = bool(config.get("ssl_verify", True))

    return cast(LegacyConfigDict, config)
