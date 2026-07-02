# Data sources

`hsg` bundles the following corpora in `assets/`:

| Corpus | File(s) | Description | Licence |
|--------|---------|-------------|---------|
| Heisig RTK | `heisig.tsv` | Remembering the Hanzi frame data (simplified) | User-compiled |
| CC-CEDICT | `cedict_ts.u8` | Community-maintained Chinese-English dictionary | CC-BY-SA 3.0 |
| Tatoeba | `tatoeba.tsv` | Sentence pairs with English translations | CC-BY 2.0 |
| HSK | `hsk_new.csv`, `hsk_old.csv` | HSK 2.0 and 3.0 vocabulary lists | Public |
| SUBTLEX-CH | `subtlex-ch/` | Subtitle-based character/word frequency | See [SUBTLEX-CH](https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/) |
| Renminwang | `renminwang/` | People's Daily newspaper frequency | See [Pleco forums](http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/) |
| Char frequency | `hanzi_by_frequency.csv` | Character frequency from corpus linguistics | See [MTSU](https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO) |

## Heisig RTK

The Heisig data (`heisig.tsv`) contains frame numbers, keywords, and pinyin
for each of the 3000 characters in *Remembering the Hanzi*. This is the
primary known-character source for `hsg`.

## CC-CEDICT

CC-CEDICT (`cedict_ts.u8`) is a community-maintained Chinese-English
dictionary with over 100,000 entries. `hsg` caches the parsed dictionary as a
pickle file (`assets/ccedict.pickle`) for faster subsequent loads.

## Tatoeba

The Tatoeba corpus (`tatoeba.tsv`) contains Chinese sentences paired with
English translations, used for the `sentences` and `random` commands.

## HSK

Two HSK vocabulary lists are bundled: `hsk_old.csv` (HSK 2.0, 6 levels) and
`hsk_new.csv` (HSK 3.0, 9 levels). Both map words and characters to
proficiency levels.

## SUBTLEX-CH

SUBTLEX-CH provides character and word frequency data derived from Chinese
film subtitles. Includes part-of-speech annotations for words. Source:
<https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/>

## Renminwang

The Renminwang corpus provides character and word frequency from the People's
Daily newspaper. Source:
<http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/>

## Character frequency

`hanzi_by_frequency.csv` is a general character frequency list from corpus
linguistics. Source:
<https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO>
