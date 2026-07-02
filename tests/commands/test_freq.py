import json

from click.testing import CliRunner


class TestFreq:
    def test_freq_all_chars(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['freq', '一二三四五六七八九十', '-t', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) > 0

    def test_freq_max_results(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['freq', '一二三四五六七八九十', '-m', '2', '-t', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) <= 2

    def test_freq_only_known(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['freq', '一二三四五六七八九十', '--only-known', '-t', 'json', '-k'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        for lemma in data:
            assert lemma['lemma'] in '一二三四五六七八九十'

    def test_freq_filter_by_text(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['freq', '一三', '-t', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        for lemma in data:
            assert lemma['lemma'] in '一三'
