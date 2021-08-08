# renminwang: http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/post-49299
# subtlex-ch: https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/

from typing import Any, Optional
from abc import ABCMeta, abstractmethod

class Frequency(metaclass=ABCMeta):

    @abstractmethod
    def find_char(self, char: str) -> Optional[list[Any]]:
        raise NotImplementedError

    @abstractmethod
    def find_word(self, word: str) -> Optional[list[Any]]:
        raise NotImplementedError