from hsg.classes.file_knownset import FileKnownSet


class TestFileKnownSet:
    def test_load_file(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n三\n')
        ks = FileKnownSet(str(f))
        assert ks.is_known('一') is True
        assert ks.is_known('二') is True
        assert ks.is_known('四') is False

    def test_is_known_additional(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n')
        ks = FileKnownSet(str(f))
        assert ks.is_known('!') is True

    def test_get_known_characters(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n')
        ks = FileKnownSet(str(f))
        chars = ks.get_known_characters()
        assert '一' in chars
        assert '!' in chars

    def test_get_statistics(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n')
        ks = FileKnownSet(str(f))
        stats = ks.get_statistics(['一', '二', '三'])
        assert stats['chars'] == 3
        assert stats['known'] == 2
