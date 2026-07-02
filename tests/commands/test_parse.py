import json

from click.testing import CliRunner


class TestParse:
    def test_parse_json(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一二三', '-t', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 3
        assert data[0]['hanzi'] == '一'

    def test_parse_csv(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一二三', '-t', 'csv'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        assert 'hanzi' in lines[0]

    def test_parse_tabulate(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一二三', '-t', 'tabulate'])
        assert result.exit_code == 0
        assert '一' in result.output

    def test_parse_only_known(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一六', '--only-known', '-t', 'json', '-m', '5'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 1
        assert data[0]['hanzi'] == '一'

    def test_parse_only_unknown(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一六', '--only-unknown', '-t', 'json', '-m', '5'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 1
        assert data[0]['hanzi'] == '六'

    def test_parse_unique(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一一一', '--unique', '-t', 'json', '-m', '5'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 1

    def test_parse_verbose(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一二三', '-v', '-t', 'json', '-m', '5'])
        assert result.exit_code == 0
        assert 'Known characters:' in result.output

    def test_parse_known_set_hsk(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['parse', '一二四', '--known-set', 'hsk', '--max', '1', '-t', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        known_chars = [d for d in data if d['known'] != '*']
        unknown_chars = [d for d in data if d['known'] == '*']
        assert any(d['hanzi'] == '一' for d in known_chars)
        assert any(d['hanzi'] == '四' for d in unknown_chars)
