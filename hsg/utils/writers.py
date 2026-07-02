import csv
import json
import sys
from abc import ABCMeta, abstractmethod
from typing import Any

import click
from tabulate import tabulate


class Writer(metaclass=ABCMeta):
    """ABC for output writers (CSV, JSON, tabulate)."""

    @abstractmethod
    def writerow(self, rowdata: list[Any]) -> None:
        """Write a single row."""

    @abstractmethod
    def writerows(self, data: list[list[Any]]) -> None:
        """Write multiple rows with headers."""


class CsvWriter(Writer):
    """TSV writer (tab-delimited CSV to stdout)."""

    def __init__(self, headers: list[str]) -> None:
        self.headers = headers
        self.writer = csv.writer(sys.stdout, delimiter='\t')

    def writerow(self, rowdata: list[Any]) -> None:
        self.writer.writerow(rowdata)

    def writerows(self, data: list[list[Any]]) -> None:
        self.writer.writerow(self.headers)
        for d in data:
            self.writer.writerow(d)


class JsonWriter(Writer):
    """JSON-lines writer (one JSON object per row, or a JSON array for writerows)."""

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def writerow(self, rowdata: list[Any]) -> None:
        row = dict(zip(self.keys, rowdata, strict=False))
        print(json.dumps(row, ensure_ascii=False))

    def writerows(self, data: list[list[Any]]) -> None:
        rows = [dict(zip(self.keys, row, strict=False)) for row in data]
        print(json.dumps(rows, ensure_ascii=False))


class TabulateWriter(Writer):
    """Pretty-printed table writer using the tabulate library."""

    def __init__(self, headers: list[str]) -> None:
        self.headers = headers

    def writerow(self, rowdata: list[Any]) -> None:
        print(tabulate(rowdata, headers=self.headers, tablefmt='github'))

    def writerows(self, data: list[list[Any]]) -> None:
        print(tabulate(data, headers=self.headers, tablefmt='github'))


# Registry of output format name -> Writer class.
WRITERS: dict[str, type[Writer]] = {
    'csv': CsvWriter,
    'json': JsonWriter,
    'tabulate': TabulateWriter,
}


def validate_fields(ctx: Any, param: Any, fields: list[str] | str) -> list[str]:
    """Click callback that validates requested output field names against the known set."""
    valid = True
    unsupported_fields: list[str] = []
    if isinstance(fields, str):
        fields = fields.split(',')
    if len(fields) == 0:
        valid = False
    for f in fields:
        if f not in ['known', 'hanzi', 'frame', 'frequency', 'hsk', 'pinyin', 'keyword', 'occurrencies']:
            valid = False
            unsupported_fields.append(f)
    if valid:
        return fields
    raise click.BadParameter(f'unsupported field(s): {", ".join(unsupported_fields)}')
