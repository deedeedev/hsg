# hsg

> Given a Chinese text, what percentage can you read — and which characters don't you know yet?

`hsg` is a command-line tool for Chinese-language learners. It analyses any
Chinese text against your **known-character set** (Heisig RTK frames, HSK
levels, a custom file, or an Anki export), reports coverage statistics, mines
comprehensible example sentences from Tatoeba, and looks up CC-CEDICT entries.

[![CI](https://github.com/deedeedev/hsg/actions/workflows/ci.yml/badge.svg)](https://github.com/deedeedev/hsg/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/hsg.svg)](https://pypi.org/project/hsg/)

---

## Quickstart

```bash
# No install needed — run directly with uvx
uvx hsg parse "你好世界"

# Or install globally
pipx install hsg
hsg parse "你好世界"
```

Output (CSV, default):

```
known	hanzi	frame	frequency	hsk	pinyin	keyword	occurrencies
yes	一	1	2	1	yī	one	1
yes	好	39	25	1	hǎo	good	1
no	世	1642	52	3	shì	world	1
no	界	1701	42	3	jiè	boundary	1
```

Use `--known-set hsk --max 3` to analyse against HSK levels instead of Heisig:

```bash
uvx hsg parse "你好世界" --known-set hsk --max 3 -t tabulate
```

## Features

- **Text coverage analysis** — paste any Chinese text, get per-character
  metadata (Heisig frame, frequency rank, HSK level, pinyin, keyword) and
  coverage stats (% known, % unknown, unique counts).
- **Pluggable known-set** — use Heisig frames (`--known-set heisig --max 30`),
  HSK levels (`--known-set hsk --max 3`), or your own character list
  (`--known-set file --known-file my_chars.txt`).
- **Comprehensible sentence mining** — pull Tatoeba sentences composed
  entirely of characters you already know. Search by keyword
  (`hsg sentences 好`) or get random samples (`hsg random -n 10`).
- **CC-CEDICT dictionary lookup** — search by simplified characters, pinyin,
  or English meaning, filtered by HSK level and frequency rank.
- **Frequency lists** — rank characters/words by SUBTLEX-CH or Renminwang
  corpus frequency, optionally filtered to unknown characters only.
- **Rich terminal output** — colourised text view (`hsg enrich`), tabulated
  tables, CSV, and JSON output formats.
- **Heisig stories** — import mnemonic stories from Anki into a JSON file
  (`hsg stories-import`), then display them per-character (`hsg stories`).
  No running Anki instance required at display time.
- **Multiple frequency corpora** — SUBTLEX-CH (subtitle-based) and
  Renminwang (newspaper-based), switchable with `--frequencies-corpus`.

## Installation

### Homebrew (macOS / Linux)

```bash
brew install deedeedev/hsg/hsg
```

### pipx (recommended)

```bash
pipx install hsg
```

### uv tool

```bash
uv tool install hsg
```

### pip

```bash
pip install hsg
```

### uvx (no install)

```bash
uvx hsg --help
```

### From source

```bash
git clone https://github.com/deedeedev/hsg.git
cd hsg
uv pip install -e ".[dev]"
```

### Optional extras

```bash
pip install hsg[clipboard]   # clipboard input fallback
```

## Usage

All commands are subcommands of the `hsg` group. Run `hsg --help` for the
full list, or `hsg <command> --help` for per-command options.

### `hsg parse` — text coverage analysis

```bash
hsg parse "你好世界"                      # default: Heisig, CSV output
hsg parse "你好世界" --known-set hsk --max 3   # use HSK levels instead
hsg parse "你好世界" --known-set file --known-file my_chars.txt
hsg parse "你好世界" -t json               # JSON output
hsg parse "你好世界" -t tabulate -s frequency  # sort by frequency, tabulated
hsg parse "你好世界" -u --only-unknown     # unique unknown characters only
hsg parse "你好世界" -v                    # include coverage stats
hsg parse -f article.txt                  # read from file
echo "你好" | hsg parse                   # read from stdin
```

Key options: `--known-set {heisig,hsk,file}`, `--max`, `--known-file`,
`-t {csv,json,tabulate}`, `-s {text,frame,frequency,occurrencies}`,
`-o/--only-known`, `-u/--only-unknown`, `-q/--unique`, `-v/--verbose`.

### `hsg enrich` — colourised text view

```bash
hsg enrich "你好世界"                     # blue = unknown Heisig, red = non-Heisig
hsg enrich "你好世界" -v                  # with coverage stats
```

### `hsg list` — Heisig frame listing

```bash
hsg list --min 1 --max 10                 # first 10 frames
hsg list --min 1 --max 100 -s frequency -r  # top 100 by frequency, descending
hsg list -f json --max-results 20         # JSON, 20 results
```

### `hsg sentences` — Tatoeba sentence search

```bash
hsg sentences 好                          # sentences containing 好
hsg sentences 好 --max 30                  # only characters in frames 1-30
hsg sentences 好 -a                        # allow all non-Heisig characters
hsg sentences 好 -n 5 -l 8                # max 5 sentences, min length 8
```

### `hsg random` — random comprehensible sentences

```bash
hsg random -m 30 -n 10                    # 10 random sentences, frames 1-30
hsg random -m 30 -n 5 -l 15 -t json       # min length 15, JSON
```

### `hsg lookup` — CC-CEDICT dictionary search

```bash
hsg lookup 你好                           # search by characters
hsg lookup ni3                            # search by pinyin
hsg lookup hello                          # search by English
hsg lookup 你好 -e -t tabulate             # exact match, tabulated
hsg lookup 好 --max-hsk 3 -m 10           # HSK 3+ only, 10 results
```

### `hsg freq` — frequency listing

```bash
hsg freq                                  # all characters by frequency
hsg freq --only-known -m 30               # only known (frames 1-30)
hsg freq --skip-known -m 30 -t json       # only unknown, JSON
hsg freq -t words -l 2                    # words, min length 2
```

### `hsg stories` / `hsg stories-import` — Heisig mnemonic stories

```bash
# One-time: import stories from Anki (requires AnkiConnect running)
hsg stories-import "你好世界" --out stories.json

# Then: display stories per character (no Anki needed)
hsg stories "你好世界" --stories-file stories.json
```

### Global options

```bash
hsg --log-level info parse "你好"          # verbose logging
python -m hsg --help                       # module invocation
```

## Data sources

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

## Comparison

| Feature | hsg | Pleco Reader | Chinese Text Analyser | Zhongwen ext | Languagecrush |
|---------|-----|--------------|----------------------|--------------|---------------|
| Text coverage % | Yes | No | Yes | No | Yes |
| Per-char metadata | Yes | Limited | Yes | Popup only | No |
| Heisig frame awareness | Yes | No | No | No | No |
| HSK level awareness | Yes | Yes | No | No | Yes |
| Custom known-set (file) | Yes | No | Yes | No | No |
| Comprehensible sentences | Yes | No | No | No | No |
| CC-CEDICT search | Yes | Yes | No | Yes | No |
| Frequency lists | Yes | No | Yes | No | No |
| Offline / CLI | Yes | No | No | Yes | No |
| Open source | Yes | No | No | Yes | No |
| Free | Yes | Freemium | Paid | Free | Freemium |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and feature requests are
welcome via [GitHub Issues](https://github.com/deedeedev/hsg/issues).

## License

Apache-2.0 — see [LICENSE](LICENSE).
