from click.testing import CliRunner


class TestEnrich:
    def test_enrich_basic(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['enrich', '一二三', '-m', '5'])
        assert result.exit_code == 0
        assert '一' in result.output
        assert '二' in result.output

    def test_enrich_unknown_in_output(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['enrich', '一六', '-m', '5'])
        assert result.exit_code == 0
        assert '一' in result.output
        assert '六' in result.output

    def test_enrich_verbose(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['enrich', '一二三', '-m', '5', '-v'])
        assert result.exit_code == 0
        assert 'Known characters:' in result.output

    def test_enrich_known_set_hsk(self, patched_constants, runner: CliRunner, app):
        result = runner.invoke(app, ['enrich', '一二四', '--known-set', 'hsk', '--max', '1'])
        assert result.exit_code == 0
        assert '一' in result.output
        assert '四' in result.output
