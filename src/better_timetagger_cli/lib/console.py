"""
### Console Output & User Interface

Functions that handle terminal output, formatting, and user interaction.
"""

import os
import subprocess
import sys
from typing import NoReturn

from rich.console import Console, Group

console = Console(highlight=False)
""" Console for default output """

stderr = Console(stderr=True, highlight=False)
""" Console for error output """


def abort(message: str | Group) -> NoReturn:
    """
    Abort the current command with a message.

    Args:
        message: The message to display before aborting.
    """
    style = "red" if isinstance(message, str) else None
    stderr.print(message, style=style)
    exit(1)


def open_in_editor(path: str, editor: str | None = None) -> None:
    """
    Open a file in the system's default editor, or a specified editor.

    Args:
        path: The path to the file to open.
        editor: The name or path of the editor executable. Default to system default.

    See:
        http://stackoverflow.com/a/72796/2271927
        http://superuser.com/questions/38984/linux-equivalent-command-for-open-command-on-mac-windows
    """
    if editor:
        subprocess.call((editor, path))

    elif sys.platform.startswith("darwin"):
        subprocess.call(("open", path))

    elif sys.platform.startswith("win"):
        if " " in path:
            subprocess.call(("start", "", path), shell=True)
        else:
            subprocess.call(("start", path), shell=True)

    elif sys.platform.startswith("linux"):
        try:
            subprocess.call(("xdg-open", path))
        except FileNotFoundError:
            subprocess.call((os.getenv("EDITOR", "nano"), path))

    else:
        stderr.print(f"\nUnsupported platform: {sys.platform}. Please open the file manually.", style="yellow")
