import click
import pytest

from hsg.utils.io import get_input


class TestGetInput:
    def test_text_argument(self):
        assert get_input('hello', None) == 'hello'

    def test_no_text_no_file_no_clipboard(self, monkeypatch):
        monkeypatch.setattr('hsg.utils.io.clipboard', None)
        monkeypatch.setattr('sys.stdin.isatty', lambda: True)
        with pytest.raises(click.UsageError):
            get_input(None, None)
