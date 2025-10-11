"""
### CLI Framework Extensions

Custom classes and utilities to extend the `click` library.
"""

from collections.abc import Iterable

import click


class AliasedCommand(click.Command):
    """
    A custom click command that supports aliases.

    Use in conjunction with `AliasedGroup` to allow commands to be invoked by multiple names.

    Example:
    ```python
        @click.group(cls=AliasedGroup)
        def cli():
            pass

        @cli.command(cls=AliasedCommand, aliases=['report', 'list', 'ls'])
        def show():
            pass
    ```
    """


    def __init__(self, *args, aliases: Iterable[str] | str | None = None, **kwargs):
        """
        Initialize with optional aliases.
        """
        super().__init__(*args, **kwargs)

        if aliases is None:
            aliases = ()
        elif isinstance(aliases, str):
            aliases = (aliases,)
        elif not isinstance(aliases, Iterable):
            raise TypeError("aliases must be a string or iterable of strings")

        self.aliases = tuple(aliases)

    def format_help(self, ctx, formatter) -> None:
        """
        Add alias section to the help output.
        """
        super().format_help(ctx, formatter)

        if self.aliases:
            with formatter.section("Aliases"):
                name_and_aliases = (self.name, *self.aliases)
                formatter.write_dl((a, "") for a in name_and_aliases)


class AliasedGroup(AliasedCommand, click.Group):
    """
    A Click group that resolves command aliases defined on the command objects.
    Also supports aliases for the group itself.

    Use in conjunction with `AliasedCommand` to allow commands to be invoked by multiple names.

    Example:
    ```python
        @click.group(cls=AliasedGroup, aliases=['db'])
        def database():
            pass

        @database.command(cls=AliasedCommand, aliases=['report', 'list', 'ls'])
        def show():
            pass
    ```
    """

    def get_command(self, ctx, cmd_name) -> click.Command | None:
        """
        Retrieve a command by its name or alias.
        """
        # Retrieve command the regular way
        command = super().get_command(ctx, cmd_name)
        if command:
            return command

        # If not found, retrieve by alias
        for cmd in self.commands.values():
            if hasattr(cmd, "aliases") and cmd_name in getattr(cmd, "aliases", ()):
                return cmd

        return None

    def resolve_command(self, ctx, args) -> tuple[str | None, click.Command | None, list[str]]:
        """
        Resolve the command name from the arguments, checking for aliases.
        """
        if args:
            cmd_name = args[0]
            resolved_cmd = self.get_command(ctx, cmd_name)
            if resolved_cmd:
                canonical_name = resolved_cmd.name
                args[0] = canonical_name
        return super().resolve_command(ctx, args)
