"""
# Global `rich` console object to render output.
"""

from rich.console import Console

console = Console(highlight=False)

stderr = Console(stderr=True, highlight=False)
