import json

from click.testing import CliRunner


class TestList:
    def test_list_json(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '3', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 3

    def test_list_csv(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '3', '-f', 'csv'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        assert 'hanzi' in lines[0]

    def test_list_max_results(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '10', '-m', '3', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) == 3

    def test_list_sort_frequency(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['list', '--min', '1', '--max', '5', '-s', 'frequency', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        freqs = [d['frequency'] for d in data]
        assert freqs == sorted(freqs)
