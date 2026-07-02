import pytest

from hsg.classes.knownset import KnownSet
from hsg.classes.knownset_factory import create_known_set


class TestKnownSetFactory:
    def test_create_heisig(self, patched_constants):
        ks = create_known_set('heisig', max=5, frequencies_corpus='subtlexch')
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_create_hsk(self, patched_constants):
        ks = create_known_set('hsk', max=2)
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_create_file(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n')
        ks = create_known_set('file', filepath=str(f))
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_invalid_backend(self):
        with pytest.raises(ValueError):
            create_known_set('bad-backend')
