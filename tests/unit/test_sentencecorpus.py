from hsg.classes.sentencecorpus import SentenceCorpus


class DummyCorpus(SentenceCorpus):
    def __init__(self):
        self._data = {'一二三': ['one two three'], '十': ['ten']}

    def load(self) -> dict[str, list[str]]:
        return self._data


class TestSentenceCorpus:
    def test_find_sentences(self):
        c = DummyCorpus()
        results = c.find_sentences('一')
        assert len(results) == 1
        assert results[0]['hanzi'] == '一二三'

    def test_find_sentences_no_match(self):
        c = DummyCorpus()
        results = c.find_sentences('九')
        assert len(results) == 0

    def test_find_sentences_with_known_chars(self):
        c = DummyCorpus()
        results = c.find_sentences('一', known_chars={'一', '二', '三'})
        assert len(results) == 1
        assert results[0]['hanzi'] == '一二三'

    def test_find_sentences_filtered_by_known_chars(self):
        c = DummyCorpus()
        results = c.find_sentences('一', known_chars={'一', '二'})
        assert len(results) == 0  # 三 not in known_chars

    def test_find_random_sentences(self):
        c = DummyCorpus()
        results = c.find_random_sentences(1, min_length=1)
        assert len(results) == 1
