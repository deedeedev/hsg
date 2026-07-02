# Usage

All commands are subcommands of the `hsg` group.

## Global options

```
--log-level [error|warning|info|debug]  Logging verbosity (default: warning).
--help                                  Show this message and exit.
```

## hsg parse

```
Usage: hsg parse [OPTIONS] [TEXT]

  Analyse Chinese text against your known-character set.

  Reads from TEXT argument, --file, or stdin (pipe).

Options:
  -f, --file FILE                     Read text from file.
  -k, --known-set TEXT                Known-character source (heisig, hsk,
                                      file).  [default: heisig]
  --known-file FILE                   Path to known-characters file (for
                                      --known-set file).
  -m, --max INTEGER                   Max frame/level for known-set.
                                      [default: all]
  -t, --format [csv|json|tabulate]    Output format.  [default: csv]
  -s, --sort [text|frame|frequency|occurrencies]
                                      Sort output by field.
  -o, --only-known                    Show only known characters.
  -u, --only-unknown                  Show only unknown characters.
  -q, --unique                        Show unique characters only.
  -v, --verbose                       Show coverage statistics.
  --help                              Show this message and exit.
```

Examples:

```bash
hsg parse "你好世界"                      # default: Heisig, CSV output
hsg parse "你好世界" --known-set hsk --max 3   # use HSK levels
hsg parse -f article.txt                  # read from file
echo "你好" | hsg parse                   # read from stdin
```

## hsg enrich

```
Usage: hsg enrich [OPTIONS] [TEXT]

  Display Chinese text with colourised character highlighting.

Options:
  -f, --file FILE                     Read text from file.
  -k, --known-set TEXT                Known-character source.
  --known-file FILE                   Path to known-characters file.
  -m, --max INTEGER                   Max frame/level for known-set.
  -v, --verbose                       Show coverage statistics.
  --help                              Show this message and exit.
```

Examples:

```bash
hsg enrich "你好世界"                     # blue = unknown, red = non-Heisig
hsg enrich "你好世界" -v                  # with coverage stats
```

## hsg list

```
Usage: hsg list [OPTIONS]

  List Heisig frames with frequency and keyword data.

Options:
  --min INTEGER                   Minimum frame number.  [default: 1]
  --max INTEGER                   Maximum frame number.  [default: all]
  -s, --sort [frame|frequency]    Sort output by field.
  -r, --reverse                   Reverse sort order.
  -f, --format [csv|json|tabulate]
                                  Output format.  [default: csv]
  --max-results INTEGER            Max results to show.  [default: all]
  --help                          Show this message and exit.
```

Examples:

```bash
hsg list --min 1 --max 10                 # first 10 frames
hsg list -f json --max-results 20         # JSON, 20 results
```

## hsg sentences

```
Usage: hsg sentences [OPTIONS] KEYWORD

  Find Tatoeba sentences containing KEYWORD.

Options:
  -m, --max-frame INTEGER          Max Heisig frame known.  [default: all]
  -a, --all-characters             Allow all non-Heisig characters.
  -n, --max-sentences INTEGER      Max sentences to return.  [default: all]
  -r, --reverse                    Return longer sentences first.
  -k, --known-set TEXT             Known-character source.
  --known-file FILE                Path to known-characters file.
  --max INTEGER                    Max frame/level for known-set.
  -f, --format [csv|json|tabulate] Output format.  [default: csv]
  --help                           Show this message and exit.
```

Examples:

```bash
hsg sentences 好                          # sentences containing 好
hsg sentences 好 --max 30                  # only frames 1-30
hsg sentences 好 -a                        # allow all non-Heisig
```

## hsg random

```
Usage: hsg random [OPTIONS]

  Return random comprehensible sentences from Tatoeba.

Options:
  -m, --max-frame INTEGER          Max Heisig frame known.
  -a, --all-characters             Allow all non-Heisig characters.
  -n, --sentences-number INTEGER   Return n sentences.  [default: 10]
  -l, --min-length INTEGER         Min sentence length.  [default: 10]
  -r, --reverse                    Return longer sentences first.
  -k, --known-set TEXT             Known-character source.
  --known-file FILE                Path to known-characters file.
  --max INTEGER                    Max frame/level for known-set.
  -f, --format [csv|json|tabulate] Output format.  [default: csv]
  --help                           Show this message and exit.
```

Examples:

```bash
hsg random -m 30 -n 10                    # 10 random sentences, frames 1-30
hsg random -m 30 -n 5 -l 15 -t json       # min length 15, JSON
```

## hsg lookup

```
Usage: hsg lookup [OPTIONS] QUERY

  Search CC-CEDICT dictionary.

Options:
  -e, --exact                      Exact match only.
  -t, --traditional                Show traditional characters.
  -f, --format [csv|json|tabulate] Output format.  [default: csv]
  -s, --sort [frequency|hsk]       Sort field.  [default: frequency]
  -r, --reverse                    Reverse sort order.
  --max-hsk TEXT                   Max HSK level.  [default: all]
  -m, --max-results INTEGER        Max results.  [default: 10]
  -a, --all                        Show all results.
  --help                           Show this message and exit.
```

Examples:

```bash
hsg lookup 你好                           # search by characters
hsg lookup ni3                            # search by pinyin
hsg lookup hello                          # search by English
hsg lookup 好 --max-hsk 3 -m 10           # HSK 3+ only, 10 results
```

## hsg freq

```
Usage: hsg freq [OPTIONS]

  List characters or words by frequency.

Options:
  -t, --format [csv|json|tabulate]  Output format.  [default: csv]
  -c, --corpus [subtlexch|renminwang]
                                    Frequency corpus.  [default: subtlexch]
  --sort [rank|frequency|count]     Sort field.  [default: rank]
  -r, --reverse                     Reverse sort order.
  -k, --known-set TEXT              Known-character source.
  --known-file FILE                 Path to known-characters file.
  --max INTEGER                     Max frame/level for known-set.
  --skip-known                      Skip known characters.
  --only-known                      Show only known characters.
  -n, --max-results INTEGER         Max results.  [default: all]
  --words                           Show words instead of characters.
  -l, --min-length INTEGER          Min word length.  [default: 1]
  --help                            Show this message and exit.
```

Examples:

```bash
hsg freq                                  # all characters by frequency
hsg freq --skip-known -m 30 -t json       # only unknown, JSON
hsg freq -t words -l 2                    # words, min length 2
```

## hsg stories

```
Usage: hsg stories [OPTIONS] [TEXT]

  Display Heisig mnemonic stories for characters in TEXT.

Options:
  --stories-file FILE    Path to JSON stories file.  [required]
  -f, --file FILE        Read text from file.
  --help                 Show this message and exit.
```

## hsg stories-import

```
Usage: hsg stories-import [OPTIONS] [TEXT]

  Import Heisig mnemonic stories from Anki via AnkiConnect.

Options:
  --out FILE             Output JSON file.  [required]
  -f, --file FILE        Read text from file.
  --help                 Show this message and exit.
```
