import csv
import json
import sys
from typing import Any

from tabulate import tabulate

from hsg.classes.frequency import Frequency
from hsg.classes.frequency_factory import create_frequency
from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS, HEISIG_CSV


class Heisig(KnownSet):
    def __init__(self, frequencies_corpus: str, maxframe: int = -1) -> None:
        self.maxframe = maxframe
        self.frequencies: Frequency = create_frequency(frequencies_corpus)
        self.heisig: dict[str, dict[str, Any]] = {}
        self.load_heisig()
        self.known_characters: list[str] = self.get_known_characters()

    def set_max_frame(self, maxframe: int) -> None:
        self.maxframe = maxframe

    def load_heisig(self) -> None:
        with open(HEISIG_CSV) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                frame = row[2]
                if frame.startswith('v') or not frame:
                    continue
                frame_num = int(frame)
                hanzi = row[0]
                keyword = row[4]
                pinyin = row[5]
                frequency_data = self.frequencies.find_char(hanzi)
                self.heisig[hanzi] = {
                    'hanzi': hanzi,
                    'frame': frame_num,
                    'keyword': keyword,
                    'pinyin': pinyin,
                    'frequency': frequency_data['rank'] if frequency_data else 9999,
                }
        if self.maxframe == -1:
            self.maxframe = max([f['frame'] for f in self.heisig.values()])

    def get_known_frames(self) -> list[str]:
        return [hanzi for hanzi in self.heisig if self.heisig[hanzi]['frame'] <= self.maxframe]

    def get_known_characters(self) -> list[str]:
        return self.get_known_frames() + list(ADDITIONAL_CHARACTERS)

    def is_known(self, char: str) -> bool:
        return char in self.known_characters

    def get_char_info(self, char: str) -> dict[str, Any]:
        return self.heisig[char]

    def get_frame_info(self, char: str) -> dict[str, Any]:
        return self.get_char_info(char)

    def output(self, words: list[dict[str, Any]], format: str) -> None:
        if format == 'csv':
            fields = ('hanzi', 'frame', 'keyword', 'pinyin', 'frequency')
            writer: csv.DictWriter[str] = csv.DictWriter(
                sys.stdout, fieldnames=fields, delimiter='\t', extrasaction='ignore'
            )
            writer.writeheader()
            writer.writerows(words)
        elif format == 'json':
            print(json.dumps(words))
        elif format == 'tabulate':
            print(tabulate(words, headers='keys', tablefmt='github'))
