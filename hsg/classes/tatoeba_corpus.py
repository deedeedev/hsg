import csv

from hsg.classes.sentencecorpus import SentenceCorpus


class TatoebaCorpus(SentenceCorpus):
    """SentenceCorpus backed by Tatoeba TSV."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._data: dict[str, list[str]] | None = None

    def load(self) -> dict[str, list[str]]:
        if self._data is not None:
            return self._data
        self._data = {}
        with open(self.filepath) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) < 4:
                    continue
                hanzi = row[1]
                english = row[3]
                if hanzi not in self._data:
                    self._data[hanzi] = [english]
                else:
                    self._data[hanzi].append(english)
        return self._data
