from abc import ABCMeta, abstractmethod
from typing import Any

from hsg.utils.constants import ADDITIONAL_CHARACTERS


class KnownSet(metaclass=ABCMeta):
    """ABC for 'which characters does the learner know'.

    Backends: Heisig (frame range), HSK (level cap), file (user list),
    anki-export (Anki deck export).
    """

    @abstractmethod
    def is_known(self, char: str) -> bool:
        """Return True if the learner knows this character."""
        raise NotImplementedError

    @abstractmethod
    def get_known_characters(self) -> list[str]:
        """Return the full list of known characters (excluding ADDITIONAL)."""
        raise NotImplementedError

    def is_additional_character(self, char: str) -> bool:
        """Return True if char is a non-Hanzi allowlist character."""
        return char in ADDITIONAL_CHARACTERS

    def get_char_info(self, char: str) -> dict[str, Any]:
        """Return backend-specific metadata for a character.

        Heisig returns {frame, keyword, pinyin, frequency}.
        HSK returns {level}. File returns {char}.
        Override in subclasses.
        """
        return {'char': char}

    def get_statistics(self, chars: list[str]) -> dict[str, Any]:
        """Compute coverage statistics for a list of characters.

        This is a concrete method — it only calls is_known(), so it
        works for any KnownSet backend.
        """
        unique_chars = [c for i, c in enumerate(chars) if c not in chars[:i]]
        total_chars = len(chars)
        total_chars_unique = len(unique_chars)
        total_known = len([c for c in chars if self.is_known(c)])
        total_known_unique = len([c for c in unique_chars if self.is_known(c)])
        total_known_percent = round(total_known / total_chars * 100, 2) if total_chars > 0 else 0
        total_known_unique_percent = (
            round(total_known_unique / total_chars_unique * 100, 2) if total_chars_unique > 0 else 0
        )
        frequencies: dict[str, dict[str, Any]] = {}
        for c in chars:
            if c not in frequencies:
                frequencies[c] = {'occurrencies': 1, 'percent': None}
            else:
                frequencies[c]['occurrencies'] += 1
        for c in frequencies:
            frequencies[c]['percent'] = round(frequencies[c]['occurrencies'] / len(chars) * 100, 2)
        return {
            'chars': total_chars,
            'known': total_known,
            'known_percent': total_known_percent,
            'unknown': total_chars - total_known,
            'unknown_percent': round(100 - total_known_percent, 2),
            'chars_unique': total_chars_unique,
            'known_unique': total_known_unique,
            'known_unique_percent': total_known_unique_percent,
            'unknown_unique': total_chars_unique - total_known_unique,
            'unknown_unique_percent': round(100 - total_known_unique_percent, 2),
            'frequencies': frequencies,
        }
