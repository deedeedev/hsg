import json
from html.parser import HTMLParser
from io import StringIO
from typing import Any


class _MLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text = StringIO()

    def handle_data(self, d: str) -> None:
        self.text.write(d)

    def get_data(self) -> str:
        return self.text.getvalue()


def _strip_tags(html: str) -> str:
    s = _MLStripper()
    s.feed(html)
    return s.get_data()


class StoryStore:
    """Disk-based story store. Reads stories from a JSON file.

    JSON format: {"<hanzi>": {"keyword": str, "keyword_ita": str, "story": str, ...}}
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        with open(self.filepath) as f:
            self._data = json.load(f)

    def get_story(self, hanzi: str) -> dict[str, Any] | None:
        entry = self._data.get(hanzi)
        if entry is None:
            return None
        story = dict(entry)
        if 'story' in story:
            story['story'] = _strip_tags(story['story'])
        return story
