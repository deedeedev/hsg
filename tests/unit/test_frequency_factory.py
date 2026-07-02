from hsg.classes.frequency import Frequency
from hsg.classes.frequency_factory import create_frequency


class TestFrequencyFactory:
    def test_create_subtlexch(self, patched_constants):
        fq = create_frequency('subtlexch')
        assert isinstance(fq, Frequency)
        assert fq.find_char('一') is not None

    def test_create_renminwang(self, patched_constants):
        fq = create_frequency('renminwang')
        assert isinstance(fq, Frequency)
        assert fq.find_char('一') is not None

    def test_invalid(self):
        import pytest

        with pytest.raises(ValueError):
            create_frequency('bad-corpus')
