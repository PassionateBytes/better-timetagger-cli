from typing import Any

from rich.console import Console
from rich.text import Text

console = Console()


def styled_padded(value: Any, width: int = 5, *, style: str = "magenta", padding_style: str = "dim magenta", padding: str = "0") -> Text:
    value_str = str(value)
    len_padding = width - len(value_str)

    if len_padding <= 0:
        return Text(value_str, style=style)
    else:
        text = Text()
        text.append(padding * len_padding, style=padding_style)
        text.append(value_str, style=style)
        return text
