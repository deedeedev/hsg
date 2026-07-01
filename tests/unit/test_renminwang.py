from hsg.classes.renminwang import RenMinWang


class TestRenMinWang:
    def test_find_char(self, patched_constants):
        r = RenMinWang()
        result = r.find_char('一')
        assert result is not None
        assert result['lemma'] == '一'
        assert result['rank'] == 1

    def test_find_char_not_found(self, patched_constants):
        r = RenMinWang()
        assert r.find_char('十') is None

    def test_find_word(self, patched_constants):
        r = RenMinWang()
        result = r.find_word('一')
        assert result is not None

    def test_get_most_frequent_lemmas(self, patched_constants):
        r = RenMinWang()
        lemmas = r.get_most_frequent_lemmas(num=3)
        assert len(lemmas) == 3
        assert lemmas[0]['rank'] == 1

    def test_get_most_frequent_lemmas_only_heisig(self, patched_constants):
        r = RenMinWang()
        lemmas = r.get_most_frequent_lemmas(only_heisig=True)
        for lemma in lemmas:
            assert lemma['lemma'] in '一二三四五六七八九十'
