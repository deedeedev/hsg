from typing import Any

from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


class FileKnownSet(KnownSet):
    """KnownSet backed by a user-supplied file (one character per line)."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._chars: set[str] = set()
        with open(filepath) as f:
            for line in f:
                char = line.strip()
                if char and len(char) == 1:
                    self._chars.add(char)

    def is_known(self, char: str) -> bool:
        return char in self._chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        return {'char': char, 'known': char in self._chars}
