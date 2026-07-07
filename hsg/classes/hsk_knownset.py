from typing import Any

from hsg.classes.hsk import HSK
from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


def _parse_level(level: str | None) -> int:
    """Parse an HSK level string into an int for max_level comparison.

    Newer HSK 3.0 rows use a range like '7-9'; we treat the lower bound
    as the level (permissive: char is 'known' at max_level >= lower bound).
    Empty/None maps to 99 (effectively unknown).
    """
    if not level:
        return 99
    if '-' in level:
        return int(level.split('-', 1)[0])
    return int(level)


class HSKKnownSet(KnownSet):
    """KnownSet backed by HSK levels.

    A character is 'known' if its HSK new-list level <= max_level,
    or if it's in ADDITIONAL_CHARACTERS.
    """

    def __init__(self, max_level: int = 6, use_old: bool = False) -> None:
        self.hsk = HSK()
        self.max_level = max_level
        self.use_old = use_old
        self._known_chars: set[str] = set(self._compute_known_chars())

    def _compute_known_chars(self) -> list[str]:
        if self.use_old:
            chars = self.hsk.get_hsk_old_chars()
            return [c for c in chars if _parse_level(self.hsk.get_hsk_old_char_level(c)) <= self.max_level]
        chars = self.hsk.get_hsk_new_chars()
        return [c for c in chars if _parse_level(self.hsk.get_hsk_new_char_level(c)) <= self.max_level]

    def is_known(self, char: str) -> bool:
        return char in self._known_chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._known_chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        level = self.hsk.get_hsk_old_char_level(char) if self.use_old else self.hsk.get_hsk_new_char_level(char)
        return {'char': char, 'level': level or ''}
