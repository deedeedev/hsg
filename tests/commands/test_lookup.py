import json

from click.testing import CliRunner


class TestLookup:
    def test_lookup_json(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['lookup', '你好', '-f', 'json', '-a'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) > 0
        assert data[0]['simplified'] == '你好'

    def test_lookup_english(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['lookup', 'hello', '-f', 'json', '-a'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert any('hello' in d['english'] for d in data)

    def test_lookup_max_results(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['lookup', '一', '-f', 'json', '-m', '1', '-a'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert len(data) <= 1
