from hsg.classes.tatoeba_corpus import TatoebaCorpus


class TestTatoebaCorpus:
    def test_load(self, patched_constants):
        tatoeba_path = str(patched_constants / 'tatoeba.tsv')
        c = TatoebaCorpus(tatoeba_path)
        data = c.load()
        assert '一二三' in data
        assert len(data['一二三']) >= 1

    def test_find_sentences(self, patched_constants):
        tatoeba_path = str(patched_constants / 'tatoeba.tsv')
        c = TatoebaCorpus(tatoeba_path)
        results = c.find_sentences('一')
        assert len(results) > 0
        assert '一' in results[0]['hanzi']
