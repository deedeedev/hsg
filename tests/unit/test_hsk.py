from hsg.classes.hsk import HSK


class TestHSK:
    def test_new_word_level(self, patched_constants):
        h = HSK()
        assert h.get_hsk_new_word_level('一') == '1'
        assert h.get_hsk_new_word_level('四') == '2'
        assert h.get_hsk_new_word_level('十') is None

    def test_old_word_level(self, patched_constants):
        h = HSK()
        assert h.get_hsk_old_word_level('一') == '1'
        assert h.get_hsk_old_word_level('三') == '2'

    def test_new_char_level(self, patched_constants):
        h = HSK()
        assert h.get_hsk_new_char_level('一') == '1'

    def test_old_char_level(self, patched_constants):
        h = HSK()
        assert h.get_hsk_old_char_level('一') == '1'

    def test_get_new_words_by_level(self, patched_constants):
        h = HSK()
        level1 = h.get_hsk_new_words('1')
        assert len(level1) == 3  # 一,二,三
        level2 = h.get_hsk_new_words('2')
        assert len(level2) == 2  # 四,五

    def test_get_old_words_by_level(self, patched_constants):
        h = HSK()
        level1 = h.get_hsk_old_words('1')
        assert len(level1) == 2  # 一,二

    def test_get_all_words(self, patched_constants):
        h = HSK()
        all_new = h.get_hsk_new_words(None)
        assert len(all_new) == 5
