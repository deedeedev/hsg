from unittest.mock import patch

from click.testing import CliRunner


class TestStories:
    @patch('hsg.commands.heisigtools.requests')
    def test_stories_no_anki(self, mock_requests, patched_constants, runner: CliRunner, app):
        """Stories should handle AnkiConnect being unavailable."""
        mock_requests.RequestException = Exception
        mock_requests.request.side_effect = Exception('connection refused')
        result = runner.invoke(app, ['stories', '一'])
        assert result.exit_code == 0
        assert 'NO HEISIG' in result.output
