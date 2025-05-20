import os
import sys
from typing import TypedDict

import click
import toml

from .rich_utils import console
from .utils import user_config_dir

CONFIG_FILE_NAME = "config.toml"
LEGACY_CONFIG_FILE_NAME = "config.txt"

DEFAULT_CONFIG = """
# Configuration for Better-TimeTagger-CLI
# Clear or remove this file to reset to factory defaults.

### API BASE URL
# This is the base URL of the TimeTagger API for your instance.
# api_url = "http://localhost:8080/timetagger/api/v2/"    # -> local instance
# api_url = "https://your.domain.net/timetagger/api/v2/"  # -> self-hosted instance
api_url = "https://timetagger.app/api/v2/"                # -> public instance

### API TOKEN
# You find your api token in the TimeTagger web application, on the account page.
api_token = "<your api token>"

### SSL CERTIFICATE VERIFICATION
# If you're self-hosting, you might need to set your own self-signed certificate or disable the verification of SSL certificate.
# Disabling the certificate verification is a potentially risky action that might expose your application to attacks.
# You can set the path to a self signed certificate for verification and validation.
# For more information, visit: https://letsencrypt.org/docs/certificates-for-localhost/
# ssl_verify = "path/to/certificate"  # -> path to self-signed certificate
# ssl_verify = false                  # -> disables SSL verification
ssl_verify = true                     # -> enables SSL verification
""".lstrip().replace("\r\n", "\n")

if sys.platform.startswith("win"):
    DEFAULT_CONFIG.replace("\n", "\r\n")


class ConfigDict(TypedDict):
    api_url: str
    api_token: str
    ssl_verify: bool | str


def get_config_path(*, legacy: bool = False) -> str:
    """
    Get the path to the config file.

    Args:
        legacy (bool): If True, return the path to the legacy config file.

    Returns:
        The path to the config file.
    """
    config_file_name = LEGACY_CONFIG_FILE_NAME if legacy else CONFIG_FILE_NAME
    return os.path.join(user_config_dir("timetagger_cli"), config_file_name)


def load_config(*, legacy: bool = False) -> ConfigDict:
    """
    Load and validate the config from the filesystem.

    Args:
        legacy (bool): If True, load the legacy config file.

    Raises:
        click.ClickException: If the config file is not found or if the config is invalid.

    Returns:
        The loaded configuration as a dictionary.
    """
    filepath = get_config_path(legacy=legacy)

    try:
        with open(filepath, "rb") as f:
            config = toml.loads(f.read().decode())

        if "api_url" not in config or not config["api_url"]:
            raise click.ClickException("Failed to load config. Parameter 'api_url' not set. Run 'timetagger setup' to fix.")
        if not config["api_url"].startswith(("http://", "https://")):
            raise click.ClickException("Failed to load config. Parameter 'api_url' must start with 'http://' or 'https://'. Run 'timetagger setup' to fix.")
        if "api_token" not in config or not config["api_token"]:
            raise click.ClickException("Failed to load config. Parameter 'api_token' not set. Run 'timetagger setup' to fix.")
        if "ssl_verify" not in config or not config["ssl_verify"]:
            config |= {"ssl_verify": True}

        return config

    except Exception as e:
        console.print(f"[red]Failed to load config file: {e.__class__.__name__}[/red]\n[dim red]{e}[/dim red]")
        raise click.Abort from e


def write_default_config(filepath: str) -> None:
    """
    Write the default config to the config file.

    If the legacy config file exists, its content is used to create the new config file.
    Otherwise, a default configuration is created.

    Args:
        filepath (str): The path to the config file.
    """
    # load content from legacy config file if it exists and is valid
    try:
        load_config(legacy=True)
        with open(get_config_path(legacy=True), "rb") as f:
            config_content = f.read().decode()
    except click.ClickException:
        config_content = DEFAULT_CONFIG

    # write default config file
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(config_content.encode())
        os.chmod(filepath, 0o640)
    except Exception as e:  # pragma: no cover
        console.print(f"[red]Could not write default config file: {e.__class__.__name__}[/red]\n[dim red]{e}[/dim red]")
        raise click.Abort from e


def prepare_config_file() -> str:
    """
    Attempt to load configuration file, or create a new one with default values
    if it doesn't exist or is empty.

    Returns:
        The path to the configuration file.
    """
    filepath = get_config_path()

    try:
        load_config()
    except click.ClickException:
        write_default_config(filepath)

    os.chmod(filepath, 0o640)
    return filepath
