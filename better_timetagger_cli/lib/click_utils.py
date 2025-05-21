from typing import NoReturn

import click
from rich import print


class AliasedGroup(click.Group):
    """
    Custom click group class that allows commands to be called by their shortest unique name.

    See: https://click.palletsprojects.com/en/stable/advanced/#command-aliases
    """

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Ambiguous command. Choose either of: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        name = cmd.name if cmd else None
        return name, cmd, args


def abort(message: str) -> NoReturn:
    """
    Abort the current command with a message.

    Args:
        message: The message to display before aborting.
    """
    print(f"\n[red]{message}[/red]")
    exit(1)
