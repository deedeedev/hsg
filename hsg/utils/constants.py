import os

# paths
UTILS_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR_PATH = os.path.join(os.path.dirname(os.path.dirname(UTILS_DIR_PATH)), 'assets')

# characters, words, sentences
HEISIG_CSV = os.path.join(ASSETS_DIR_PATH, 'heisig.tsv')
CCEDICT_CSV = os.path.join(ASSETS_DIR_PATH, 'cedict_ts.u8')
TATOEBA_CSV = os.path.join(ASSETS_DIR_PATH, 'tatoeba.tsv')
TATOEBA_DB = os.path.join(ASSETS_DIR_PATH, 'tatoeba.sqlite')
HSK_NEW_CSV = os.path.join(ASSETS_DIR_PATH, 'hsk_new.csv')
HSK_OLD_CSV = os.path.join(ASSETS_DIR_PATH, 'hsk_old.csv')

# frequencies
FREQUENCIES_CSV = os.path.join(ASSETS_DIR_PATH, 'hanzi_by_frequency.csv')
RMW_FREQUENCIES_CHARS_CSV = os.path.join(ASSETS_DIR_PATH, 'renminwang/RENMINWANG-CHR')
RMW_FREQUENCIES_WORDS_CSV = os.path.join(ASSETS_DIR_PATH, 'renminwang/RENMINWANG-WF')
SUBTLEX_CH_CHARS_CSV = os.path.join(ASSETS_DIR_PATH, 'subtlex-ch/SUBTLEX-CH-CHR.csv')
SUBTLEX_CH_WORDS_CSV = os.path.join(ASSETS_DIR_PATH, 'subtlex-ch/SUBTLEX-CH-WF.csv')
SUBTLEX_CH_WORDS_POS_COMBINED_CSV = os.path.join(ASSETS_DIR_PATH, 'subtlex-ch/SUBTLEX_CH_131210_CE.utf8')

# misc
ADDITIONAL_CHARACTERS = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    'àáèéìíòóùú'
    '1234567890'
    ' !?#%()[]-_,;:.=\'"“”…‘’'
    '１６８！。？，、；：％（）《》〈〉【】〖〗〔〕「」『』—·℃'
)
