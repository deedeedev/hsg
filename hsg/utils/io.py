import sys
from typing import Any

import click

try:
    import clipboard
except ImportError:
    clipboard = None


def get_input(text: str | None, file: Any) -> str:
    """Gets input from argument, then stdin, then clipboard."""
    if text:
        return text
    elif file and not sys.stdin.isatty():
        with file:
            result: str = file.read()
            return result
    else:
        if clipboard is None:
            raise click.UsageError(
                "no text argument or stdin provided and the 'clipboard' "
                'extra is not installed; install with `pip install hsg[clipboard]`'
            )
        clip_text: str = clipboard.paste()
        return clip_text
