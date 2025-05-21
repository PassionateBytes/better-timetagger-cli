from collections.abc import Iterable
from typing import NoReturn

import click
from rich import print


class AliasedGroup(click.Group):
    """
    Custom click group class that allows commands to be called by their shortest unique name.

    See: https://click.palletsprojects.com/en/stable/advanced/#command-aliases
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._alias_map = {}

    def add_command(self, cmd, name=None):
        # Get all names (primary + aliases)
        if name and isinstance(name, str):
            names = (name,)
        elif name and isinstance(name, Iterable):
            names = tuple(name)
        elif cmd.name and isinstance(cmd.name, str):
            names = (cmd.name,)
        elif cmd.name and isinstance(cmd.name, Iterable):
            names = tuple(cmd.name)
        else:
            names = (cmd.callback.__name__,)

        # Set the primary name (the first one)
        primary = names[0] if name is None else name
        cmd.name = primary
        super().add_command(cmd, primary)

        # Register aliases
        for alias in names[1:]:
            self._alias_map[alias] = primary

    def get_command(self, ctx, cmd_name) -> click.Command | None:
        # Resolve alias if required
        if cmd_name in self._alias_map:
            cmd_name = self._alias_map[cmd_name]

        # Try direct match
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # Fallback to shortest unique prefix
        matches = [
            x
            for x in self.list_commands(ctx)
            if x.startswith(cmd_name) or any(alias.startswith(cmd_name) for alias in self._alias_map if self._alias_map[alias] == x)
        ]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Ambiguous command. Choose either of: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args) -> tuple[str | None, click.Command | None, list[str]]:
        # Resolve alias before handing off
        if args:
            first = args[0]
            if first in self._alias_map:
                args[0] = self._alias_map[first]
        return super().resolve_command(ctx, args)


def abort(message: str) -> NoReturn:
    """
    Abort the current command with a message.

    Args:
        message: The message to display before aborting.
    """
    print(f"\n[red]{message}[/red]")
    exit(1)
