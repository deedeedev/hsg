import random as _random
from abc import ABCMeta, abstractmethod
from typing import Any


class SentenceCorpus(metaclass=ABCMeta):
    """ABC for sentence corpora (Tatoeba, CC-CEDICT examples, etc.)."""

    @abstractmethod
    def load(self) -> dict[str, list[str]]:
        """Load sentences into a {hanzi: [translations]} dict."""
        raise NotImplementedError

    def find_sentences(
        self,
        keyword: str,
        known_chars: set[str] | None = None,
        max_sentences: int = 10000,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Find sentences containing keyword, optionally filtered by known set."""
        data = self.load()
        sentences: list[dict[str, Any]] = []
        for hanzi, translations in data.items():
            if keyword not in hanzi:
                continue
            if known_chars is not None and not all(c in known_chars for c in hanzi):
                continue
            sentences.append({'hanzi': hanzi, 'translations': translations})
        sentences.sort(key=lambda x: len(x['hanzi']), reverse=reverse)
        return sentences[:max_sentences]

    def find_random_sentences(
        self,
        number: int,
        min_length: int = 10,
        known_chars: set[str] | None = None,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Find random sentences of minimum length, optionally filtered."""
        data = self.load()
        candidates: list[dict[str, Any]] = []
        for hanzi, translations in data.items():
            if len(hanzi) < min_length:
                continue
            if known_chars is not None and not all(c in known_chars for c in hanzi):
                continue
            candidates.append({'hanzi': hanzi, 'translations': translations})
        if len(candidates) < number:
            number = len(candidates)
        sampled = _random.sample(candidates, number)
        sampled.sort(key=lambda x: len(x['hanzi']), reverse=reverse)
        return sampled
