import json

from click.testing import CliRunner


class TestOutputFormats:
    def test_list_csv_snapshot(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '3', '-f', 'csv'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        assert lines[0] == 'hanzi\tframe\tkeyword\tpinyin\tfrequency'
        assert lines[1].startswith('一\t1\tOne\tyi1\t')
        assert lines[2].startswith('二\t2\tTwo\ter4\t')
        assert lines[3].startswith('三\t3\tThree\tsan1\t')

    def test_list_json_snapshot(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '3', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert data[0]['hanzi'] == '一'
        assert data[0]['frame'] == 1
        assert data[0]['keyword'] == 'One'
        assert data[0]['pinyin'] == 'yi1'
        assert data[1]['hanzi'] == '二'
        assert data[2]['hanzi'] == '三'

    def test_freq_csv_snapshot(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['freq', '一二', '-m', '2', '-t', 'csv'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        assert lines[0].rstrip('\r').startswith('lemma\tcount\t')
