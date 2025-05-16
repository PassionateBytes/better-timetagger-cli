import os
import sys
from typing import Any, TypedDict
from webbrowser import get

import click
import toml

from .utils import user_config_dir

CONFIG_FILE_NAME = "config.toml"

DEFAULT_CONFIG = """
# Configuration for Better-TimeTagger-CLI
# Clear or remove this file to reset to factory defaults.

# Set the API URL
api_url = "https://timetagger.app/api/v2/"  # public instance
# api_url = "http://localhost:8080/timetagger/api/v2/"  # local instance
# api_url = "https://timetagger.example.net/timetagger/api/v2/"  # self-hosted instance

# Set your API Token
# Go to the account page, copy the token, paste it here (between the quotes).
api_token = ""

# SSL Certificate Verification
# If you're self-hosting, you might need to set your own self-signed certificate or disable the verification of SSL certificate.
# Disabling the certificate verification is a potentially risky action that might expose your application to attacks.
# You can set the path to a self signed certificate for verification and validation:
# For more information, visit: https://letsencrypt.org/docs/certificates-for-localhost/
ssl_verify = true
# ssl_verify = "path/to/certificate"  # self-signed certificate
""".lstrip().replace("\r\n", "\n")

if sys.platform.startswith("win"):
    DEFAULT_CONFIG.replace("\n", "\r\n")


class ConfigDict(TypedDict):
    api_url: str
    api_token: str
    ssl_verify: bool | str


def get_config_path() -> str:
    """
    Get the path to the config file.

    Returns:
        The path to the config file.
    """
    return os.path.join(user_config_dir("timetagger_cli"), CONFIG_FILE_NAME)


def load_config() -> ConfigDict:
    """
    Load and validate the config from the filesystem.

    Raises:
        RuntimeError: If the config file is not found or if the config is invalid.

    Returns:
        The loaded configuration as a dictionary.
    """
    filename = get_config_path()

    if not os.path.isfile(filename):
        raise click.Abort("Failed to load configuration file. Run 'timetagger setup' to fix.")

    with open(filename, "rb") as f:
        config = toml.loads(f.read().decode())

    if "api_url" not in config:
        raise click.Abort("Failed to load config. Parameter 'api_url' not set. Run 'timetagger setup' to fix.")
    if not config["api_url"].startswith(("http://", "https://")):
        raise click.Abort("Failed to load config. Parameter 'api_url' must start with 'http://' or 'https://'. Run 'timetagger setup' to fix.")
    if "api_token" not in config:
        raise click.Abort("Failed to load config. Parameter 'api_token' not set. Run 'timetagger setup' to fix.")
    if "ssl_verify" not in config:
        config |= {"ssl_verify": True}

    return config


def write_default_config() -> None:
    """
    Write the default config to the config file.
    """
    filename = get_config_path()

    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(DEFAULT_CONFIG.encode())
        # Config file contains user secret so it should not be readable to others
        os.chmod(filename, 0o640)
    except Exception as e:  # pragma: no cover
        print(f"Could not write default config file: {e}")


def prepare_config_file() -> str:
    """
    Attempt to load configuration file, or create a new one with default values
    if it doesn't exist or is empty.

    Returns:
        The path to the configuration file.
    """
    filename = get_config_path()

    try:
        if os.path.isfile(filename):
            with open(filename, "rb") as f:
                text = f.read().strip()
            if not text:
                write_default_config()
        else:
            write_default_config()
        os.chmod(filename, 0o640)
    except Exception as e:  # pragma: no cover
        raise click.Abort(f"Failed to create default config file: {e.__class__.__name__} - {e}") from e

    return filename
