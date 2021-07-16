# anki -> pleco dictionary
# preleva da anki le storie per ogni carattere e le aggiunge al dizionario pleco rsh-pleco-pinyin.txt

import sys
import csv
import json
import re
import requests

from rich import print


class Anki:

    def __init__(self):
        pass

    # restituisce una lista di id in base ad una query
    def find_notes(self, hanzi):
        url = "http://localhost:8765"
        payload = {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": f"deck:Cinese::Heisig Hanzi:{hanzi}",
            }
        }
        response = requests.request("POST", url, json=payload)
        ids = json.loads(response.text)["result"]
        return ids

    # restituisce una nota in base all'id
    def get_note(self, id):
        url = "http://localhost:8765"
        payload = {
            "action": "notesInfo",
            "version": 6,
            "params": {
                "notes": [id],
            }
        }
        response = requests.request("POST", url, json=payload)
        notes = json.loads(response.text)["result"]
        if len(notes) > 0:
            return notes[0]
        return None
    
    def get_data(self, hanzi):
        ids = self.find_notes(hanzi)
        if ids:
            note = self.get_note(ids[0])
            if note:
                return (
                        note['fields']['Story']['value'],
                        note['fields']['KeywordIta']['value'],
                        note['fields']['PrimitiveMeaningIta']['value'],
                    )
        return None


class PlecoDict:

    PLECO_NEWLINE = "\uEAB1"
    PLECO_BOLD_OPEN = "\uEAB2"
    PLECO_BOLD_CLOSE = "\uEAB3"
    PLECO_ITALIC_OPEN = "\uEAB4"
    PLECO_ITALIC_CLOSE = "\uEAB5"
    PLECO_UNDERLINE_OPEN = "\uEAB6"
    PLECO_UNDERLINE_CLOSE = "\uEAB7"
    PLECO_LINK_OPEN = "\uEAB8"
    PLECO_LINK_CLOSE = "\uEABB\u200B"
    PLECO_INVERT_OPEN = "\uEABC"
    PLECO_INVERT_CLOSE = "\uEABD"
    PLECO_ALTFONT_OPEN = "\uEABE"
    PLECO_ALTFONT_CLOSE = "\uEABF"
    PLECO_COLOR_OPEN = "\uEAC1"  # followed by four characters (Pleco 3.2.26/Android)
    PLECO_COLOR_CLOSE = "\uEAC2"
    PLECO_BLOCK_OPEN = "\uEAC3"  # followed by four characters (Pleco 3.2.26/Android)
    PLECO_BLOCK_CLOSE = "\uEAC4"
    PLECO_SIZE_OPEN = "\uEAC5"  # followed by four characters (Pleco 3.2.26/Android)
    PLECO_SIZE_CLOSE = "\uEAC6"
    PLECO_HR = "\uEAC7" # followed by four characters (Pleco 3.2.26/Android)

    def __init__(self, plecodictcsv):
        self.plecodictcsv = plecodictcsv
        self.rows = []
        self.loadplecodict()

    def loadplecodict(self):
        with open(self.plecodictcsv, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            self.first_row = next(reader)[0] # skip first line
            for row in reader:
                self.rows.append({
                        'hanzi': row[0],
                        'pinyin': row[1],
                        'text': row[2],
                    })
    
    def italic(self, text):
        return self.PLECO_ITALIC_OPEN + text + self.PLECO_ITALIC_CLOSE
    
    def altfont(self, text):
        return self.PLECO_ALTFONT_OPEN + text + self.PLECO_ALTFONT_CLOSE
    
    def linkify(self, text):
        return self.PLECO_LINK_OPEN + text + self.PLECO_LINK_CLOSE
    
    # replaces html tags with pleco special characters
    def normalize_mnemonic(self, mnemonic):
        mnemonic = mnemonic.replace('&nbsp;', ' ')
        mnemonic = mnemonic.replace('<i>', self.PLECO_ITALIC_OPEN).replace('</i>', self.PLECO_ITALIC_CLOSE)
        mnemonic = mnemonic.replace('<em>', self.PLECO_ITALIC_OPEN).replace('</em>', self.PLECO_ITALIC_CLOSE)
        mnemonic = re.sub(r"\((.)\)", "(" + self.linkify(r"\1") + ")", mnemonic)
        mnemonic = re.sub(r"\((.),\s?(.)\)", "(" + self.linkify(r"\1") + ", " + self.linkify(r"\2") + ")", mnemonic)
        return mnemonic
    
    # add mnemonic story
    def append_mnemonic(self, text, mnemonic):
        mnemonic = self.normalize_mnemonic(mnemonic)
        mnemonic = self.altfont('MNEMONIC') + " " + mnemonic + self.PLECO_BLOCK_CLOSE + self.PLECO_BLOCK_OPEN
        parts = text.split(' $  ')
        parts.insert(len(parts)-1, mnemonic) # add mnemonic before NAVIGATION section
        return ' $  '.join(parts)
    
    # add italian keyword and primitive meaning translations
    def append_translation(self, text, keyword_ita, primitive_ita):
        parts = text.split(' $  ')
        translation = keyword_ita
        if primitive_ita:
            translation += ' ❖ ' + primitive_ita
        translation += self.PLECO_NEWLINE + self.PLECO_BLOCK_OPEN
        parts[0] = parts[0].rstrip(self.PLECO_BLOCK_OPEN) + translation
        return ' $  '.join(parts)


if __name__ == '__main__':
    pd = PlecoDict('assets/rsh-pleco-pinyin.txt')
    anki = Anki()
    writer = csv.writer(sys.stdout, delimiter='\t')
    print(pd.first_row) # header
    for i, row in enumerate(pd.rows):
        # if row['hanzi'] == '容':
        if len(row['hanzi']) == 1: # filter lemmas with links to chapters and lessons
            data = anki.get_data(row['hanzi'])
            if data:
                mnemonic, keyword_ita, primitive_ita = data
                row['text'] = pd.append_mnemonic(row['text'], mnemonic)
                row['text'] = pd.append_translation(row['text'], keyword_ita, primitive_ita)
        writer.writerow(row.values())


"""
'one ❖ floor; ceiling\ueab1\ueac3',
'\ueabePINYIN\ueabf yī \ueabeJYUTPING\ueabf jat1\ueac4\ueac3',
'\ueabeSTORY\ueabf [1]\ueac4\ueac3',
'❖ Also known as: \ueab4floor\ueab5. \ueab4ceiling\ueab5.\ueac4\ueac3',
'\ueabeFRAME\ueabf 1, \ueabeLESSON\ueabf 1, \ueabeBOOK\ueabf 1, \ueabePAGE\ueabf 19\ueac4\ueac3',
'\ueabeNAVIGATION\ueabf ↑Lesson 1↑ (\ueab8本书1第1课\ueabb\u200b) »two» (\ueab8二\ueabb\u200b)\ueac4'
"""

"""
one ❖ floor; ceiling\ueab1\ueac3
 $  \ueabePINYIN\ueabf yī \ueabeJYUTPING\ueabf jat1\ueac4\ueac3
 $  \ueabeSTORY\ueabf [1]\ueac4\ueac3
 $  ❖ Also known as: \ueab4floor\ueab5. \ueab4ceiling\ueab5.\ueac4\ueac3
 $  \ueabeFRAME\ueabf 1, \ueabeLESSON\ueabf 1, \ueabeBOOK\ueabf 1, \ueabePAGE\ueabf 19\ueac4\ueac3
 $  \ueabeNAVIGATION\ueabf ↑Lesson 1↑ (\ueab8本书1第1课\ueabb\u200b​) »two» (\ueabb二\u200b​)\ueac4
"""