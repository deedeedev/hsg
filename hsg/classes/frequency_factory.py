from hsg.classes.frequency import Frequency


def create_frequency(corpus: str) -> Frequency:
    """Create a Frequency instance by corpus name."""
    if corpus == 'renminwang':
        from hsg.classes.renminwang import RenMinWang

        return RenMinWang()
    if corpus == 'subtlexch':
        from hsg.classes.subtlexch import SubtlexCh

        return SubtlexCh()
    raise ValueError(f'unknown frequency corpus: {corpus}')
