import sys

import click

try:
    import clipboard
except ImportError:
    clipboard = None


def get_input(text, file):
    """
    Gets input from argument, then stdin, then clipboard.
    """
    if text:
        # text argument
        return text
    elif file and not sys.stdin.isatty():
        with file:
            # 1st fallback: stdin
            return file.read()
    else:
        # 2nd fallback: clipboard
        if clipboard is None:
            raise click.UsageError(
                "no text argument or stdin provided and the 'clipboard' "
                'extra is not installed; install with `pip install hsg[clipboard]`'
            )
        return clipboard.paste()
