import os

UTILS_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR_PATH = os.path.join(os.path.dirname(UTILS_DIR_PATH), 'assets')

HEISIG_CSV = os.path.join(ASSETS_DIR_PATH, 'heisig.tsv')
FREQUENCIES_CSV = os.path.join(ASSETS_DIR_PATH, 'hanzi_by_frequency.csv')
TATOEBA_CSV = os.path.join(ASSETS_DIR_PATH, 'tatoeba.tsv')

HSK_NEW_CSV = os.path.join(ASSETS_DIR_PATH, 'hsk_new.csv')
HSK_OLD_CSV = os.path.join(ASSETS_DIR_PATH, 'hsk_old.csv')

CCEDICT_CSV = os.path.join(ASSETS_DIR_PATH, 'cedict_ts.u8')

RMW_FREQUENCIES_CHARS_CSV = os.path.join(ASSETS_DIR_PATH, 'renminwang/RENMINWANG-CHR')
RMW_FREQUENCIES_WORDS_CSV = os.path.join(ASSETS_DIR_PATH, 'renminwang/RENMINWANG-WF')

ADDITIONAL_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàáèéìíòóùú1234567890 !?#%()[]-_,;:.=\'"“”…‘’１６８！。？，、；：％（）《》〈〉【】〖〗〔〕「」『』—·℃'