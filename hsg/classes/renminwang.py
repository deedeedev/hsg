import csv
from typing import Any

from hsg.classes.frequency import Frequency
from hsg.utils.constants import RMW_FREQUENCIES_CHARS_CSV, RMW_FREQUENCIES_WORDS_CSV


class RenMinWang(Frequency):
    """Frequency corpus based on Renminwang (People's Daily) newspaper data.

    Provides character and word frequency data from the renminwang/ assets.
    """

    def __init__(self) -> None:
        """Load character and word frequency CSVs."""
        self.char_freq: list[dict[str, Any]] = self.load_csv(RMW_FREQUENCIES_CHARS_CSV)
        self.word_freq: list[dict[str, Any]] = self.load_csv(RMW_FREQUENCIES_WORDS_CSV)
        self.chars: dict[str, Any] = self.create_dict(self.char_freq)
        self.words: dict[str, Any] = self.create_dict(self.word_freq)

    def load_csv(self, csvfile: str) -> list[dict[str, Any]]:
        """Parse a Renminwang frequency TSV, skipping header lines."""
        with open(csvfile) as f:
            fields = (
                'lemma',
                'count',
                'count_million',
                'count_log',
                'cd',
                'cd_percent',
                'cd_log',
                'rank',
                'count_x_cd',
            )
            reader = csv.DictReader(f, fieldnames=fields, delimiter='\t')
            reader_no_headers = list(reader)[3:]  # skip first 3 lines
            for idx, lemma in enumerate(reader_no_headers):
                lemma['rank'] = idx + 1
                lemma['count_x_cd'] = int(lemma['count']) * int(lemma['cd'])
            return reader_no_headers

    def create_dict(self, lemmas: list[dict[str, Any]]) -> dict[str, Any]:
        """Build a lemma-to-record lookup dict from a list."""
        result: dict[str, Any] = {}
        for lemma in lemmas:
            result[lemma['lemma']] = lemma
        return result

    def find_char(self, char: str) -> dict[str, Any] | None:
        """Look up frequency data for a character. Returns None if not found."""
        return self.chars.get(char)

    def find_word(self, word: str) -> dict[str, Any] | None:
        """Look up frequency data for a word. Returns None if not found."""
        return self.words.get(word)

    def get_most_frequent_lemmas(
        self,
        type: str = 'chars',
        num: int = -1,
        skip_known: set[str] | None = None,
        only_known: set[str] | None = None,
        min_length: int = 1,
        sort: str = 'rank',
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Return ranked lemmas, optionally filtered by known-set membership."""
        lemmas = self.char_freq if type == 'chars' else self.word_freq
        if num == -1:
            num = len(lemmas)
        if skip_known is not None:
            lemmas = [lemma for lemma in lemmas if lemma['lemma'] not in skip_known]
        if only_known is not None:
            lemmas = [lemma for lemma in lemmas if lemma['lemma'] in only_known]
        data = sorted(lemmas, key=lambda x: x[sort], reverse=reverse)
        return data[:num]
