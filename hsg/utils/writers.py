import csv
import json
import sys
from abc import ABCMeta, abstractmethod
from typing import Any

import click
from tabulate import tabulate


class Writer(metaclass=ABCMeta):
    @abstractmethod
    def writerow(self, rowdata: list[Any]) -> None:
        pass

    @abstractmethod
    def writerows(self, data: list[list[Any]]) -> None:
        pass


class CsvWriter(Writer):
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
    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def writerow(self, rowdata: list[Any]) -> None:
        row = dict(zip(self.keys, rowdata, strict=False))
        print(json.dumps(row, ensure_ascii=False))

    def writerows(self, data: list[list[Any]]) -> None:
        rows = [dict(zip(self.keys, row, strict=False)) for row in data]
        print(json.dumps(rows, ensure_ascii=False))


class TabulateWriter(Writer):
    def __init__(self, headers: list[str]) -> None:
        self.headers = headers

    def writerow(self, rowdata: list[Any]) -> None:
        print(tabulate(rowdata, headers=self.headers, tablefmt='github'))

    def writerows(self, data: list[list[Any]]) -> None:
        print(tabulate(data, headers=self.headers, tablefmt='github'))


WRITERS: dict[str, type[Writer]] = {
    'csv': CsvWriter,
    'json': JsonWriter,
    'tabulate': TabulateWriter,
}


def validate_fields(ctx: Any, param: Any, fields: list[str] | str) -> list[str]:
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
