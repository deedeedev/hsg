# https://goeastmandarin.com/new-hsk-levels
# old https://github.com/gigacool/hanyu-shuiping-kaoshi/blob/master/hsk.csv

import csv
from typing import Optional, Union, Any

from collections import OrderedDict
from utils.constants import HSK_OLD_CSV, HSK_NEW_CSV, ADDITIONAL_CHARACTERS


class HSK:

    def __init__(self, oldhskcsv: str, newhskcsv: str) -> None:
        self.hsk_old: OrderedDict = OrderedDict()
        self.hsk_new: OrderedDict = OrderedDict()
        self.hsk_old_chars: OrderedDict = OrderedDict()
        self.hsk_new_chars: OrderedDict = OrderedDict()
        self.load_old_hsk(oldhskcsv)
        self.load_new_hsk(newhskcsv)

    def load_old_hsk(self, oldhskcsv: str) -> None:
        with open(oldhskcsv, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)
            for row in reader:
                level, num, simplified, pinyin, translations = row
                self.hsk_old[simplified] = {
                    'level': level,
                    'num': int(num),
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'translations': translations.replace(',', ';')
                }
                for c in simplified:
                    if c not in ADDITIONAL_CHARACTERS and c not in self.hsk_old_chars:
                        self.hsk_old_chars[c] = level

    def load_new_hsk(self, newhskcsv: str) -> None:
        with open(newhskcsv, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)
            for row in reader:
                level, num, simplified, pinyin, translations, pos, example, alternative, multiple = row
                self.hsk_new[simplified] = {
                    'level': level,
                    'num': int(num),
                    'simplified': simplified,
                    'pinyin': pinyin,
                    'translations': translations,
                    # 'pos': pos,
                    # 'example': example,
                    # 'alternative': alternative,
                    # 'multiple': multiple,
                }
                for c in simplified:
                    if c not in ADDITIONAL_CHARACTERS and c not in self.hsk_new_chars:
                        self.hsk_new_chars[c] = level

    def get_hsk_old_word(self, char: str) -> Optional[dict]:
        return self.hsk_old.get(char)

    def get_hsk_new_word(self, char: str) -> Optional[dict]:
        return self.hsk_new.get(char)
    
    def get_hsk_old_words(self, level: Optional[Union[str, int]]) -> list[dict[str, Union[str, int]]]:
        if level:
            return [w for w in self.hsk_old.values() if w['level'] == str(level)]
        return list(self.hsk_old.values())

    def get_hsk_new_words(self, level: Optional[Union[str, int]]) -> list[dict[str, Union[str, int]]]:
        if level:
            return [w for w in self.hsk_new.values() if w['level'] == str(level)]
        return list(self.hsk_new.values())
    
    def get_hsk_old_word_level(self, word: str) -> Optional[str]:
        if word in self.hsk_old:
            return self.hsk_old[word]['level']
        return None

    def get_hsk_new_word_level(self, word: str) -> Optional[str]:
        if word in self.hsk_new:
            return self.hsk_new[word]['level']
        return None

    def get_hsk_old_char_level(self, char: str) -> Optional[str]:
        return self.hsk_old_chars.get(char)

    def get_hsk_new_char_level(self, char: str) -> Optional[str]:
        return self.hsk_new_chars.get(char)

    def get_hsk_old_chars(self, level: Optional[Union[str, int]] = None) -> Optional[list[str]]:
        if level:
            return [c for c in self.hsk_old_chars if self.hsk_old_chars[c] == str(level)]
        return list(self.hsk_old_chars.keys())

    def get_hsk_new_chars(self, level: Optional[Union[str, int]] = None) -> Optional[list[str]]:
        if level:
            return [c for c in self.hsk_new_chars if self.hsk_new_chars[c] == str(level)]
        return list(self.hsk_new_chars.keys())


if __name__ == '__main__':
    hsk = HSK(HSK_OLD_CSV, HSK_NEW_CSV)

    # print(hsk.get_hsk_old_char_level('爱'))
    # print(hsk.get_hsk_old_chars(2))
    # print(len(hsk.get_hsk_old_chars()))

    # print(hsk.get_hsk_new_char_level('爱'))
    # print(hsk.get_hsk_new_chars('7-9'))
    # print(len(hsk.get_hsk_new_chars()))

    # print(hsk.get_hsk_old_word('认真'))
    # print(hsk.get_hsk_new_word('认真'))

    # print(hsk.get_hsk_old_words(1))
    # print(hsk.get_hsk_new_words(1))

    # print(hsk.get_hsk_old_word_level('认真'))
    # print(hsk.get_hsk_new_word_level('认真'))