import csv
from collections import OrderedDict
from typing import Any

from hsg.utils.constants import ADDITIONAL_CHARACTERS, HSK_NEW_CSV, HSK_OLD_CSV


class HSK:
    """HSK vocabulary data reader (both HSK 2.0 old and HSK 3.0 new lists).

    Loads word and character data from hsk_old.csv and hsk_new.csv.
    Provides level lookups for words and individual characters.
    """

    def __init__(self) -> None:
        """Load both HSK old and new lists."""
        self.hsk_old: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hsk_new: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hsk_old_chars: OrderedDict[str, str] = OrderedDict()
        self.hsk_new_chars: OrderedDict[str, str] = OrderedDict()
        self.load_old_hsk(HSK_OLD_CSV)
        self.load_new_hsk(HSK_NEW_CSV)

    def load_old_hsk(self, oldhskcsv: str) -> None:
        """Parse the HSK 2.0 word list into self.hsk_old."""
        with open(oldhskcsv) as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)
            for row in reader:
                level, num, simplified, pinyin, translations = row
                self.hsk_old[simplified] = {
                    'level': level,
                    'num': int(num),
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'translations': translations.replace(',', ';'),
                }
                for c in simplified:
                    if c not in ADDITIONAL_CHARACTERS and c not in self.hsk_old_chars:
                        self.hsk_old_chars[c] = level

    def load_new_hsk(self, newhskcsv: str) -> None:
        """Parse the HSK 3.0 word list into self.hsk_new."""
        with open(newhskcsv) as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for row in reader:
                level, num, simplified, pinyin, translations = row
                self.hsk_new[simplified] = {
                    'level': level,
                    'num': int(num),
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'translations': translations,
                }
                for c in simplified:
                    if c not in ADDITIONAL_CHARACTERS and c not in self.hsk_new_chars:
                        self.hsk_new_chars[c] = level

    def get_hsk_old_word(self, char: str) -> dict[str, Any] | None:
        """Look up a word in the HSK 2.0 list. Returns None if not found."""
        return self.hsk_old.get(char)

    def get_hsk_new_word(self, char: str) -> dict[str, Any] | None:
        """Look up a word in the HSK 3.0 list. Returns None if not found."""
        return self.hsk_new.get(char)

    def get_hsk_old_words(self, level: str | int | None) -> list[dict[str, Any]]:
        """Return HSK 2.0 words at the given level (None = all levels)."""
        if level:
            return [w for w in self.hsk_old.values() if w['level'] == str(level)]
        return list(self.hsk_old.values())

    def get_hsk_new_words(self, level: str | int | None) -> list[dict[str, Any]]:
        """Return HSK 3.0 words at the given level (None = all levels)."""
        if level:
            return [w for w in self.hsk_new.values() if w['level'] == str(level)]
        return list(self.hsk_new.values())

    def get_hsk_old_word_level(self, word: str) -> str | None:
        """Return the HSK 2.0 level for a word, or None."""
        if word in self.hsk_old:
            level: str = self.hsk_old[word]['level']
            return level
        return None

    def get_hsk_new_word_level(self, word: str) -> str | None:
        """Return the HSK 3.0 level for a word, or None."""
        if word in self.hsk_new:
            level: str = self.hsk_new[word]['level']
            return level
        return None

    def get_hsk_old_char_level(self, char: str) -> str | None:
        """Return the HSK 2.0 level for a single character, or None."""
        return self.hsk_old_chars.get(char)

    def get_hsk_new_char_level(self, char: str) -> str | None:
        """Return the HSK 3.0 level for a single character, or None."""
        return self.hsk_new_chars.get(char)

    def get_hsk_old_chars(self, level: str | int | None = None) -> list[str]:
        """Return HSK 2.0 characters at the given level (None = all)."""
        if level:
            return [c for c in self.hsk_old_chars if self.hsk_old_chars[c] == str(level)]
        return list(self.hsk_old_chars.keys())

    def get_hsk_new_chars(self, level: str | int | None = None) -> list[str]:
        """Return HSK 3.0 characters at the given level (None = all)."""
        if level:
            return [c for c in self.hsk_new_chars if self.hsk_new_chars[c] == str(level)]
        return list(self.hsk_new_chars.keys())
