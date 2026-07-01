from hsg.classes.subtlexch import SubtlexCh


class TestSubtlexCh:
    def test_find_char(self, patched_constants):
        s = SubtlexCh()
        result = s.find_char('一')
        assert result is not None
        assert result['lemma'] == '一'
        assert result['rank'] == 1

    def test_find_char_not_found(self, patched_constants):
        s = SubtlexCh()
        assert s.find_char('十') is None

    def test_find_word(self, patched_constants):
        s = SubtlexCh()
        result = s.find_word('一')
        assert result is not None
        assert result['lemma'] == '一'

    def test_get_most_frequent_lemmas(self, patched_constants):
        s = SubtlexCh()
        lemmas = s.get_most_frequent_lemmas(num=3)
        assert len(lemmas) == 3
        assert lemmas[0]['rank'] == 1
        assert lemmas[1]['rank'] == 2
        assert lemmas[2]['rank'] == 3

    def test_get_most_frequent_lemmas_only_heisig(self, patched_constants):
        s = SubtlexCh()
        lemmas = s.get_most_frequent_lemmas(only_heisig=True)
        for lemma in lemmas:
            assert lemma['lemma'] in '一二三四五六七八九十'

    def test_get_most_frequent_lemmas_sorted_by_count(self, patched_constants):
        s = SubtlexCh()
        lemmas = s.get_most_frequent_lemmas(sort='count', reverse=True)
        assert lemmas[0]['count'] >= lemmas[-1]['count']

    def test_find_pos(self, patched_constants):
        s = SubtlexCh()
        # POS file skip-3 eats 的,我; 一,二,三 remain
        result = s.find_pos('一')
        assert result is not None
        assert result[0] == 'n'
