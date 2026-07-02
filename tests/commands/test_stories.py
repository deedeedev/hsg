import json

from click.testing import CliRunner


class TestStories:
    def test_stories_no_file(self, patched_constants, runner: CliRunner, app):
        """Stories without --stories-file should error."""
        result = runner.invoke(app, ['stories', '一'])
        assert result.exit_code != 0

    def test_stories_with_file(self, patched_constants, runner: CliRunner, app, tmp_path):
        """Stories should read from a JSON file."""
        data = {
            '一': {'keyword': 'One', 'keyword_ita': 'Uno', 'story': 'One story'},
        }
        f = tmp_path / 'stories.json'
        f.write_text(json.dumps(data))

        result = runner.invoke(app, ['stories', '一', '--stories-file', str(f)])
        assert result.exit_code == 0
        assert 'One' in result.output

    def test_stories_no_story(self, patched_constants, runner: CliRunner, app, tmp_path):
        """Stories should report NO STORY for chars not in the file."""
        f = tmp_path / 'stories.json'
        f.write_text('{}')

        result = runner.invoke(app, ['stories', '三', '--stories-file', str(f)])
        assert result.exit_code == 0
        assert 'NO STORY' in result.output


class TestStoriesImport:
    def test_stories_import(self, tmp_path, runner: CliRunner, app, monkeypatch):
        """stories import should write a JSON file from AnkiConnect data."""
        output_file = tmp_path / 'stories.json'

        import hsg.commands.heisigtools as ht_mod

        class FakeResponse:
            def __init__(self, data: str):
                self.text = data

        def fake_request(method, url, json=None, timeout=None, **kw):
            if json and json.get('action') == 'findNotes':
                return FakeResponse('{"result": [1], "error": null}')
            elif json and json.get('action') == 'notesInfo':
                return FakeResponse(
                    '{"result": [{"fields": {"Keyword": {"value": "One"}, '
                    '"KeywordIta": {"value": "Uno"}, "PrimitiveMeaning": {"value": ""}, '
                    '"PrimitiveMeaningIta": {"value": ""}, "Story": {"value": "<b>One</b>"}}}], '
                    '"error": null}'
                )
            return FakeResponse('{"result": [], "error": null}')

        monkeypatch.setattr(ht_mod.requests, 'request', fake_request)
        monkeypatch.setattr(ht_mod.requests, 'RequestException', Exception)

        result = runner.invoke(app, ['stories-import', '一', '--out', str(output_file)])
        assert result.exit_code == 0
        data = json.loads(output_file.read_text())
        assert '一' in data
        assert data['一']['keyword'] == 'One'
