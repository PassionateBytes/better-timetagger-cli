"""
# Utilities load and interact with the configuration file.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, cast, overload
from urllib.parse import urlparse, urlunparse

import toml

from .misc import abort
from .types import ConfigDict, LegacyConfigDict

CONFIG_FILE = "config.toml"
LEGACY_CONFIG_FILE = "config.txt"

DEFAULT_CONFIG_TEMPLATE = """
# Configuration for Better-TimeTagger-CLI
# Clear or remove this file to reset to factory defaults.

### TIMETAGGER URL
# This is the base URL of the TimeTagger API for your instance.
# base_url = "http://localhost:8080/timetagger/"  # -> local instance
# base_url = "https://your.domain.net/timetagger/"  # -> self-hosted instance
base_url = "{base_url}"  # -> public instance

### API TOKEN
# You find your api token in the TimeTagger web application, on the account page.
api_token = "{api_token}"

### SSL CERTIFICATE VERIFICATION
# If you're self-hosting, you might need to set your own self-signed certificate or disable the verification of SSL certificate.
# Disabling the certificate verification is a potentially risky action that might expose your application to attacks.
# You can set the path to a self signed certificate for verification and validation.
# For more information, visit: https://letsencrypt.org/docs/certificates-for-localhost/
# ssl_verify = "path/to/certificate"  # -> path to self-signed certificate
# ssl_verify = false  # -> disables SSL verification
ssl_verify = {ssl_verify}  # -> enables SSL verification

### DATE/TIME FORMAT
# This format-string is used to render dates and times in the command line interface.
# For more information, visit: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
# datetime_format = "%Y-%m-%dT%H:%M:%S"  # -> ISO 8601 format
# datetime_format = "%d.%m.%Y %H:%M"  # -> European date with 24hr time
# datetime_format = "%m/%d/%Y %I:%M %P"  # -> US-American date with 12hr am/pm time
datetime_format = "{datetime_format}"  # -> Custom format with abbreviated month and custom styling

### WEEKDAY FORMAT
# This format-string is used to render weekdays in the command line interface.
# For more information, visit: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
# weekday_format = "%A"  # -> full weekday name
weekday_format = "{weekday_format}"  # -> abbreviated weekday name
""".lstrip().replace("\r\n", "\n")

DEFAULT_CONFIG_DATA = {
    "base_url": "https://timetagger.io/timetagger/",
    "api_token": "<your api token>",
    "ssl_verify": "true",
    "datetime_format": "%d-%b-%Y [bold]%H:%M[/bold]",
    "weekday_format": "%a",
}

if sys.platform.startswith("win"):  # pragma: no cover
    DEFAULT_CONFIG_TEMPLATE.replace("\n", "\r\n")


_CONFIG_CACHE: ConfigDict | None = None


@overload
def load_config(*, abort_on_error: Literal[True] = True, cache: bool = True) -> ConfigDict: ...


@overload
def load_config(*, abort_on_error: Literal[False] = False, cache: bool = True) -> ConfigDict | None: ...


def load_config(*, abort_on_error: bool = True, cache=True) -> ConfigDict | None:
    """
    Load and validate the config from the filesystem.

    Cache the configuration by default to avoid reloading it multiple times.

    Args:
        abort_on_error: Set to False to return None instead of aborting the program on loading errors.
        cache: Set to False to force reloading the config file.

    Returns:
        The loaded configuration as a dictionary.
    """
    global _CONFIG_CACHE
    if cache and _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    filepath = get_config_path(CONFIG_FILE)

    try:
        with open(filepath, "rb") as f:
            config = toml.loads(f.read().decode())

        if "base_url" not in config or not config["base_url"]:
            raise ValueError("Parameter 'base_url' not set.")
        if not config["base_url"].startswith(("http://", "https://")):
            raise ValueError("Parameter 'base_url' must start with 'http://' or 'https://'.")
        if "api_token" not in config or not config["api_token"]:
            raise ValueError("Parameter 'api_token' not set.")
        if "ssl_verify" not in config or not config["ssl_verify"]:
            config |= {"ssl_verify": True}
        if "datetime_format" not in config:
            raise ValueError("Parameter 'datetime_format' not set.")
        if not validate_strftime_format(config["datetime_format"]):
            raise ValueError("Parameter 'datetime_format' is invalid.")
        if "weekday_format" not in config:
            raise ValueError("Parameter 'weekday_format' not set.")
        if not validate_strftime_format(config["weekday_format"]):
            raise ValueError("Parameter 'weekday_format' is invalid.")

    except Exception as e:
        if abort_on_error:
            abort(f"Failed to load config file: {e.__class__.__name__}\n[dim]{e}\nRun 'timetagger setup' to fix.[/dim]")
        return None

    _CONFIG_CACHE = cast(ConfigDict, config)
    return cast(ConfigDict, config)


def load_legacy_config() -> LegacyConfigDict | None:
    """
    Load and validate the legacy config from the filesystem.

    Returns:
        The loaded configuration as a dictionary. None if the config is invalid or not reachable.
    """
    try:
        filepath = get_config_path(LEGACY_CONFIG_FILE)
        with open(filepath, "rb") as f:
            config = toml.loads(f.read().decode())

        if (
            "api_url" not in config
            or not config["api_url"]
            or not config["api_url"].startswith(("http://", "https://"))
            or "api_token" not in config
            or not config["api_token"]
        ):
            raise Exception("Invalid configuration values.")
        if "ssl_verify" not in config or not config["ssl_verify"]:
            config |= {"ssl_verify": True}

    except Exception:
        return None

    return cast(LegacyConfigDict, config)


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


def create_default_config() -> str:
    """
    Create a new configuration file.
    Grab default values from the legacy config file if possible. Otherwise, use the default values.

    Returns:
        The path to the configuration file.
    """

    # load legacy config values
    try:
        legacy_config_values = load_legacy_config()
        if legacy_config_values:
            url = urlparse(legacy_config_values["api_url"])
            url_path = Path(url.path).parent.parent
            url = url._replace(path=str(url_path))
            base_url = urlunparse(url).rstrip("/") + "/"
            config_data = {
                **DEFAULT_CONFIG_DATA,
                "base_url": base_url,
                "api_token": legacy_config_values["api_token"],
                "ssl_verify": "true" if legacy_config_values["ssl_verify"] else "false",
            }

        else:
            raise Exception("Could not load legacy config.")

    # fallback to default values
    except Exception:
        config_data = DEFAULT_CONFIG_DATA

    # write config file
    try:
        filepath = get_config_path(CONFIG_FILE)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(DEFAULT_CONFIG_TEMPLATE.format(**config_data).encode())
        os.chmod(filepath, 0o640)
        return filepath

    except Exception as e:
        abort(f"Could not create default config file: {e.__class__.__name__}\n[dim]{e}[/dim]")


def ensure_config_file() -> str:
    """
    Ensure that the configuration file exists and is valid.
    If necessary, create a new configuration file with default values.

    Returns:
        The path to the configuration file.
    """
    if not load_config(abort_on_error=False):
        filepath = create_default_config()
    else:
        filepath = get_config_path(CONFIG_FILE)

    os.chmod(filepath, 0o640)
    return filepath


def get_config_path(config_file: str) -> str:
    """
    Get the path to the config file.

    Args:
        config_file: The name of the config file.

    Returns:
        The path to the config file.
    """
    return os.path.join(get_config_dir(), "timetagger_cli", config_file)


def get_config_dir(roaming=False) -> str:
    """
    Get the directory to store app config files.

    Args:
        roaming: If True, use roaming profile on Windows.

    Returns:
        The path to the config directory.
    """
    if sys.platform.startswith("darwin"):
        path = os.path.expanduser("~/Library/Preferences/")

    elif sys.platform.startswith("win"):
        path1, path2 = os.getenv("LOCALAPPDATA"), os.getenv("APPDATA")
        path = (path2 or path1) if roaming else (path1 or path2)
        path = os.path.normpath(path)

    else:
        path = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    if not (path and os.path.isdir(path)):
        path = os.path.expanduser("~")

    return str(path)
