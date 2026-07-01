import json

from click.testing import CliRunner


class TestRandom:
    def test_random_json(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['random', '-a', '-n', '2', '-l', '1', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip(), strict=False)
        assert len(data) <= 2

    def test_random_min_length(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['random', '-a', '-n', '1', '-l', '3', '-f', 'json'])
        assert result.exit_code == 0
        if result.output.strip():
            data = json.loads(result.output.strip(), strict=False)
            for s in data:
                assert len(s['hanzi']) >= 3
