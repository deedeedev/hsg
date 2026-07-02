# hanzi_by_frequency.csv frequencies: https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO
# renminwang: http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/post-49299
# subtlex-ch: https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/

from abc import ABCMeta, abstractmethod
from typing import Any


class Frequency(metaclass=ABCMeta):
    """ABC for character/word frequency corpora.

    Backends: SubtlexCh (subtitle-based), RenMinWang (newspaper-based).
    """

    @abstractmethod
    def find_char(self, char: str) -> dict[str, Any] | None:
        """Look up frequency data for a single character. Returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_word(self, word: str) -> dict[str, Any] | None:
        """Look up frequency data for a multi-character word. Returns None if not found."""
        raise NotImplementedError

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
        """Return ranked lemmas, optionally filtered by known-set membership.

        Args:
            type: 'chars' or 'words'.
            num: Max results (-1 = all).
            skip_known: Exclude these characters.
            only_known: Include only these characters.
            min_length: Minimum lemma length.
            sort: Sort key ('rank' or 'frequency').
            reverse: Descending order if True.
        """
        raise NotImplementedError
