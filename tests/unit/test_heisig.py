from hsg.classes.heisig import Heisig


class TestHeisig:
    def test_is_known(self, patched_constants):
        h = Heisig('subtlexch', 5)
        assert h.is_known('一') is True
        assert h.is_known('六') is False  # frame 6 > maxframe 5

    def test_is_known_additional(self, patched_constants):
        h = Heisig('subtlexch', 3)
        assert h.is_known('!') is True  # ADDITIONAL_CHARACTERS

    def test_get_frame_info(self, patched_constants):
        h = Heisig('subtlexch', 10)
        info = h.get_frame_info('一')
        assert info['frame'] == 1
        assert info['keyword'] == 'One'
        assert info['pinyin'] == 'yi1'

    def test_get_known_frames(self, patched_constants):
        h = Heisig('subtlexch', 3)
        frames = h.get_known_frames()
        assert '一' in frames
        assert '二' in frames
        assert '三' in frames
        assert '四' not in frames

    def test_get_statistics(self, patched_constants):
        h = Heisig('subtlexch', 5)
        stats = h.get_statistics(['一', '一', '二', '六'])
        assert stats['chars'] == 4
        assert stats['known'] == 3  # 一,一,二
        assert stats['unknown'] == 1  # 六
        assert stats['known_percent'] == 75.0

    def test_get_statistics_empty(self, patched_constants):
        h = Heisig('subtlexch', 5)
        stats = h.get_statistics([])
        assert stats['chars'] == 0
        assert stats['known_percent'] == 0

    def test_load_heisig_skips_variant_rows(self, patched_constants):
        h = Heisig('subtlexch', -1)
        assert len(h.heisig) == 10  # 10 real frames, no variant rows
