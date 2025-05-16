import os
import subprocess
import sys

import click


def open_file(path: str, editor: str | None = None) -> None:
    """
    Open a file in the system's default editor or a specified editor.

    Args:
        path: The path to the file to open.
        editor: The name or path of the editor executable. Default to system default.
    """
    if editor:
        subprocess.call((editor, path))
        return

    if sys.platform.startswith("darwin"):
        subprocess.call(("open", path))

    elif sys.platform.startswith("win"):
        if " " in path:
            # see: http://stackoverflow.com/a/72796/2271927
            subprocess.call(("start", "", path), shell=True)
        else:
            subprocess.call(("start", path), shell=True)

    elif sys.platform.startswith("linux"):
        try:
            # see: http://superuser.com/questions/38984/linux-equivalent-command-for-open-command-on-mac-windows
            subprocess.call(("xdg-open", path))
        except FileNotFoundError:
            subprocess.call((os.getenv("EDITOR", "vi"), path))

    else:
        click.echo(f"Edit the file at: {path}")


def user_config_dir(appname=None, roaming=False) -> str:
    """
    Get the directory to store app config files.

    Args:
        appname: The name of the application subdirectory.
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

    if appname:
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    return str(path)
