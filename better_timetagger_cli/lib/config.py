import os
import sys
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

import toml

from .utils import abort, get_config_dir


class ConfigDict(TypedDict):
    base_url: str
    api_token: str
    ssl_verify: bool | str


class LegacyConfigDict(TypedDict):
    api_url: str
    api_token: str
    ssl_verify: bool | str


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
""".lstrip().replace("\r\n", "\n")

DEFAULT_CONFIG_VALUES: ConfigDict = {
    "base_url": "https://timetagger.io/timetagger/",
    "api_token": "<your api token>",
    "ssl_verify": "True",
}

if sys.platform.startswith("win"):
    DEFAULT_CONFIG_TEMPLATE.replace("\n", "\r\n")


def get_config_path(config_file: str) -> str:
    """
    Get the path to the config file.

    Args:
        config_file: The name of the config file.

    Returns:
        The path to the config file.
    """
    return os.path.join(get_config_dir(), "timetagger_cli", config_file)


def load_config(*, abort_on_error: bool = True) -> ConfigDict:
    """
    Load and validate the config from the filesystem.

    Args:
        abort_on_error: Set to False to return None instead of aborting the program on loading errors.

    Returns:
        The loaded configuration as a dictionary.
    """
    filepath = get_config_path(CONFIG_FILE)

    try:
        with open(filepath, "rb") as f:
            config = toml.loads(f.read().decode())

        if "base_url" not in config or not config["base_url"]:
            raise Exception("Parameter 'base_url' not set. Run 'timetagger setup' to fix.")
        if not config["base_url"].startswith(("http://", "https://")):
            raise Exception("Parameter 'base_url' must start with 'http://' or 'https://'. Run 'timetagger setup' to fix.")
        if "api_token" not in config or not config["api_token"]:
            raise Exception("Parameter 'api_token' not set. Run 'timetagger setup' to fix.")
        if "ssl_verify" not in config or not config["ssl_verify"]:
            config |= {"ssl_verify": True}

        return config

    except Exception as e:
        if abort_on_error:
            abort(f"Failed to load config file: {e.__class__.__name__}\n[dim]{e}[/dim]")
        return None


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

        return config

    except Exception:
        return None


def create_default_config() -> None:
    """
    Create a new configuration file.
    Grab default values from the legacy config file if possible. Otherwise, use the default values.
    """

    # load legacy config values
    try:
        legacy_config_values = load_legacy_config()
        if legacy_config_values:
            url = urlparse(legacy_config_values["api_url"])
            url_path = Path(url.path).parent.parent
            url = url._replace(path=str(url_path))
            config_values: ConfigDict = {
                "base_url": urlunparse(url),
                "api_token": legacy_config_values["api_token"],
                "ssl_verify": legacy_config_values["ssl_verify"],
            }

        else:
            raise Exception("Could not load legacy config.")

    # fallback to default values
    except Exception:
        config_values = DEFAULT_CONFIG_VALUES

    # write config file
    try:
        filepath = get_config_path(CONFIG_FILE)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(DEFAULT_CONFIG_TEMPLATE.format(**config_values).encode())
        os.chmod(filepath, 0o640)

    except Exception as e:
        abort(f"Could not create default config file: {e.__class__.__name__}\n[dim]{e}[/dim]")


def ensure_config_file() -> str:
    """
    Ensure that the configuration file exists and is valid.
    If necessary, create a new configuration file with default values.

    Returns:
        The path to the configuration file.
    """
    filepath = get_config_path(CONFIG_FILE)

    if not load_config(abort_on_error=False):
        create_default_config(filepath)

    os.chmod(filepath, 0o640)
    return filepath
