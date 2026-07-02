from typing import Any

from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


class DummyKnownSet(KnownSet):
    def __init__(self, chars: set[str]) -> None:
        self._chars = chars

    def is_known(self, char: str) -> bool:
        return char in self._chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        return {'char': char}


class TestKnownSetABC:
    def test_is_known(self):
        ks = DummyKnownSet({'一', '二'})
        assert ks.is_known('一') is True
        assert ks.is_known('三') is False
        assert ks.is_known('!') is True  # additional

    def test_is_additional_character(self):
        ks = DummyKnownSet(set())
        assert ks.is_additional_character('!') is True
        assert ks.is_additional_character('一') is False

    def test_get_statistics(self):
        ks = DummyKnownSet({'一', '二'})
        stats = ks.get_statistics(['一', '一', '二', '三'])
        assert stats['chars'] == 4
        assert stats['known'] == 3
        assert stats['unknown'] == 1
        assert stats['known_percent'] == 75.0

    def test_get_statistics_empty(self):
        ks = DummyKnownSet(set())
        stats = ks.get_statistics([])
        assert stats['chars'] == 0
        assert stats['known_percent'] == 0
