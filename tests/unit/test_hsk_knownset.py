from hsg.classes.hsk_knownset import HSKKnownSet


class TestHSKKnownSet:
    def test_is_known(self, patched_constants):
        ks = HSKKnownSet(max_level=2)
        assert ks.is_known('一') is True  # level 1
        assert ks.is_known('四') is True  # level 2
        assert ks.is_known('十') is False  # not in fixture

    def test_is_known_additional(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        assert ks.is_known('!') is True

    def test_get_known_characters(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        chars = ks.get_known_characters()
        assert '一' in chars
        assert '!' in chars  # ADDITIONAL_CHARACTERS

    def test_get_char_info(self, patched_constants):
        ks = HSKKnownSet(max_level=3)
        info = ks.get_char_info('一')
        assert info['level'] == '1'

    def test_get_statistics(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        stats = ks.get_statistics(['一', '二', '四'])
        assert stats['chars'] == 3
        assert stats['known'] == 2  # 一,二 are level 1; 四 is level 2
