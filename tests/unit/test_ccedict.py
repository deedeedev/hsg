from hsg.classes.ccedict import Ccedict


class TestCcedict:
    def test_get_query_type_hanzi(self, patched_constants):
        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        assert c.get_query_type('你好') == 'simplified'

    def test_get_query_type_pinyin(self, patched_constants):
        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        assert c.get_query_type('ni3') == 'pinyin'

    def test_get_query_type_english(self, patched_constants):
        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        assert c.get_query_type('hello') == 'english'

    def test_load_dict(self, patched_constants):
        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        assert len(c.dictionary) == 5
        assert c.dictionary[0]['simplified'] == '你好'

    def test_parse_line_english(self, patched_constants):
        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        entry = [d for d in c.dictionary if d['simplified'] == '你好'][0]
        assert entry['pinyin'] == 'ni3 hao3'
        assert 'hello' in entry['english']

    def test_sort_key(self, patched_constants):
        import sys

        c = Ccedict(str(patched_constants / 'cedict_ts.u8'), 'subtlexch')
        assert c.sort_key('') == sys.maxsize
        assert c.sort_key('3') == 3
        assert c.sort_key('7-9') == 7
