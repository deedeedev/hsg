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

    def test_load_real_format_9_cols(self, patched_constants, assets_dir, monkeypatch):
        """Real assets/hsk_new.csv has 9 cols; loader must accept extra columns."""
        import os

        monkeypatch.setattr('hsg.classes.hsk.HSK_NEW_CSV', os.path.join(str(assets_dir), 'hsk_new_real.csv'))
        h = HSK()
        assert h.get_hsk_new_word_level('一') == '1'
        assert h.get_hsk_new_word_level('三') == '2'
        assert h.get_hsk_new_word_level('十') is None
        word = h.get_hsk_new_word('一')
        assert word is not None
        assert word['translations'] == 'one; 1'
