import json

from click.testing import CliRunner


class TestSentences:
    def test_sentences_csv(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['sentences', '一', '-m', '5', '-f', 'csv'])
        assert result.exit_code == 0
        lines = result.output.strip().split('\n')
        assert len(lines) >= 1

    def test_sentences_json(self, patched_constants, runner: CliRunner, app):
        # TODO(phase2): rich.print wraps long JSON lines, use strict=False
        result = runner.invoke(app, ['sentences', '一', '-m', '5', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip(), strict=False)
        assert len(data) > 0

    def test_sentences_all_characters(self, patched_constants, runner: CliRunner, app):
        # TODO(phase2): rich.print wraps long JSON lines, use strict=False
        result = runner.invoke(app, ['sentences', '一', '-a', '-m', '5', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip(), strict=False)
        assert len(data) > 0

    def test_sentences_known_set_hsk(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['sentences', '一', '--known-set', 'hsk', '--max', '2', '-f', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output.strip(), strict=False)
        assert len(data) > 0

    def test_sentences_known_set_file(self, patched_constants, runner: CliRunner, app, tmp_path):
        known_file = tmp_path / 'known.txt'
        known_file.write_text('一\n二\n三\n')
        result = runner.invoke(
            app,
            ['sentences', '一', '--known-set', 'file', '--known-file', str(known_file), '-f', 'json'],
        )
        assert result.exit_code == 0
        data = json.loads(result.output.strip(), strict=False)
        for s in data:
            assert all(c in '一二三' or c in '!?,. ' for c in s['hanzi'])
