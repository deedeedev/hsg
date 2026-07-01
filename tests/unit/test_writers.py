import json

import click
import pytest

from hsg.utils.writers import CsvWriter, JsonWriter, TabulateWriter, validate_fields


class TestCsvWriter:
    def test_writerows(self, capsys):
        w = CsvWriter(['a', 'b'])
        w.writerows([[1, 2], [3, 4]])
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert lines[0].rstrip('\r') == 'a\tb'
        assert lines[1].rstrip('\r') == '1\t2'
        assert lines[2].rstrip('\r') == '3\t4'


class TestJsonWriter:
    def test_writerows_valid_json(self, capsys):
        w = JsonWriter(['hanzi', 'frame'])
        w.writerows([['一', 1], ['二', 2]])
        captured = capsys.readouterr()
        data = json.loads(captured.out.strip())
        assert len(data) == 2
        assert data[0] == {'hanzi': '一', 'frame': 1}

    def test_writerow_valid_json(self, capsys):
        w = JsonWriter(['hanzi', 'frame'])
        w.writerow(['一', 1])
        captured = capsys.readouterr()
        data = json.loads(captured.out.strip())
        assert data == {'hanzi': '一', 'frame': 1}


class TestTabulateWriter:
    def test_writerows(self, capsys):
        w = TabulateWriter(['a', 'b'])
        w.writerows([[1, 2], [3, 4]])
        captured = capsys.readouterr()
        assert 'a' in captured.out
        assert 'b' in captured.out


class TestValidateFields:
    def test_valid_fields(self):
        result = validate_fields(None, None, 'hanzi,frame,frequency')
        assert result == ['hanzi', 'frame', 'frequency']

    def test_invalid_field(self):
        with pytest.raises(click.BadParameter):
            validate_fields(None, None, 'badfield')
