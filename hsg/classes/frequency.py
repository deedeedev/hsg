# hanzi_by_frequency.csv frequencies: https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO
# renminwang: http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/post-49299
# subtlex-ch: https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/

from abc import ABCMeta, abstractmethod
from typing import Any


class Frequency(metaclass=ABCMeta):
    @abstractmethod
    def find_char(self, char: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def find_word(self, word: str) -> dict[str, Any] | None:
        raise NotImplementedError
