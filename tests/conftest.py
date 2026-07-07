import os
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from hsg.cli import cli

# ---------------------------------------------------------------------------
# Tiny asset fixtures
# ---------------------------------------------------------------------------

HEISIG_TSV = (
    '一\t\t1\t1\tOne\tyi1\n'
    '二\t\t2\t2\tTwo\ter4\n'
    '三\t\t3\t3\tThree\tsan1\n'
    '四\t\t4\t4\tFour\tsi4\n'
    '五\t\t5\t5\tFive\twu3\n'
    '六\t\t6\t6\tSix\tliu4\n'
    '七\t\t7\t7\tSeven\tqi1\n'
    '八\t\t8\t8\tEight\tba1\n'
    '九\t\t9\t9\tNine\tjiu3\n'
    '十\t\t10\t10\tTen\tshi2\n'
)

# 5-column CSV (code unpacks exactly 5; real file has 9 cols — TODO(phase2))
HSK_NEW_CSV = (
    'level,num,simplified,pinyin,definitions\n'
    '1,0001,一,yi1,one\n'
    '1,0002,二,er4,two\n'
    '1,0003,三,san1,three\n'
    '2,0004,四,si4,four\n'
    '2,0005,五,wu3,five\n'
)

# 9-column CSV matching the real assets/hsk_new.csv format
HSK_NEW_CSV_REAL = (
    'level,num,simplified,pinyin,definitions,pos,example,alternative,multiple\n'
    '1,0001,一,yi1,one; 1,n,,,,,\n'
    '1,0002,二,er4,two; 2,n,,,,,\n'
    '2,0003,三,san1,three; 3,n,,,,,\n'
)

HSK_OLD_CSV = (
    'Level\tIdentifier\tHanzi\tPinYin\tTranslations\n'
    '1\t1\t一\tyi1\tone, 1\n'
    '1\t2\t二\ter4\ttwo, 2\n'
    '2\t3\t三\tsan1\tthree, 3\n'
    '2\t4\t四\tsi4\tfour, 4\n'
)

TATOEBA_TSV = (
    '1\t一二三\t100\tone two three\n'
    '2\t四五六\t200\tfour five six\n'
    '3\t七八九十\t300\tseven eight nine ten\n'
    '4\t一二三\t400\tone two three again\n'
    '5\t十\t500\tten\n'
)

CEDICT_U8 = (
    '#! time=1234567890\n'
    '你好 你好 [ni3 hao3] /hello/hi/\n'
    '再见 再见 [zai4 jian4] /goodbye/see you again/\n'
    '一 一 [yi1] /one/1/single/a(n)/\n'
    '二 二 [er4] /two/2/\n'
    '三 三 [san1] /three/3/\n'
)

# SubtlexCh: 2 metadata + 1 header = 3 skip lines, then data
SUBTLEX_CHR = (
    '"Total character count: 100",,,,,,\n'
    '"Context number: 5",,,,,,\n'
    'Character\tCHRCount\tCHR/million\tlogCHR\tCHR-CD\tCHR-CD%\tlogCHR-CD\n'
    '一\t100\t50.0\t1.7\t5\t100\t0.3\n'
    '二\t90\t45.0\t1.65\t5\t100\t0.3\n'
    '三\t80\t40.0\t1.6\t4\t80\t0.3\n'
    '四\t70\t35.0\t1.54\t4\t80\t0.3\n'
    '五\t60\t30.0\t1.48\t3\t60\t0.3\n'
)

SUBTLEX_WF = (
    '"Total word count: 100",,,,,,\n'
    '"Context number: 5",,,,,,\n'
    'Word\tWCount\tW/million\tlogW\tW-CD\tW-CD%\tlogW-CD\n'
    '一\t100\t50.0\t1.7\t5\t100\t0.3\n'
    '二\t90\t45.0\t1.65\t5\t100\t0.3\n'
    '三\t80\t40.0\t1.6\t4\t80\t0.3\n'
)

# POS file: 1 header only (skip-3 eats 2 data rows as in production)
SUBTLEX_POS = (
    'Word\tLength\tPinyin\tPinyin.Input\tWCount\tW.million\tlog10W\t'
    'W-CD\tW-CD%\tlog10CD\tDominant.PoS\tDominant.PoS.Freq\t'
    'All.PoS\tAll.PoS.Freq\tEng.Tran.\n'
    '的\t1\tde5\tde\t100\t50.0\t1.7\t5\t100\t0.3\tu\t100\t.u.\t.100.\t"of"\n'
    '我\t1\two3\two\t90\t45.0\t1.65\t5\t100\t0.3\tr\t90\t.r.\t.90.\tI/me\n'
    '一\t1\tyi1\tyi\t80\t40.0\t1.6\t4\t80\t0.3\tn\t80\t.n.\t.80.\tone\n'
    '二\t1\ter4\ter\t70\t35.0\t1.54\t4\t80\t0.3\tn\t70\t.n.\t.70.\ttwo\n'
    '三\t1\tsan1\tsan\t60\t30.0\t1.48\t3\t60\t0.3\tn\t60\t.n.\t.60.\tthree\n'
)

# RenMinWang: 2 metadata + 1 header = 3 skip lines, then data
RMW_CHR = (
    '"Total character count: 100"\n'
    '"Context number: 5"\n'
    'Character\tCHRCount\tCHR/million\tlogCHR\tCHR-CD\tCHR-CD%\tlogCHR-CD\n'
    '一\t100\t50.0\t1.7\t5\t100\t0.3\n'
    '二\t90\t45.0\t1.65\t5\t100\t0.3\n'
    '三\t80\t40.0\t1.6\t4\t80\t0.3\n'
    '四\t70\t35.0\t1.54\t4\t80\t0.3\n'
    '五\t60\t30.0\t1.48\t3\t60\t0.3\n'
)

RMW_WF = (
    '"Total word count: 100"\n'
    '"Context number: 5"\n'
    'Word\tWCount\tW/million\tlogW\tW-CD\tW-CD%\tlogW-CD\n'
    '一\t100\t50.0\t1.7\t5\t100\t0.3\n'
    '二\t90\t45.0\t1.65\t5\t100\t0.3\n'
    '三\t80\t40.0\t1.6\t4\t80\t0.3\n'
)


@pytest.fixture(scope='session')
def assets_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a tmp directory with miniature asset files."""
    d = tmp_path_factory.mktemp('assets')
    (d / 'heisig.tsv').write_text(HEISIG_TSV)
    (d / 'hsk_new.csv').write_text(HSK_NEW_CSV)
    (d / 'hsk_new_real.csv').write_text(HSK_NEW_CSV_REAL)
    (d / 'hsk_old.csv').write_text(HSK_OLD_CSV)
    (d / 'tatoeba.tsv').write_text(TATOEBA_TSV)
    (d / 'cedict_ts.u8').write_text(CEDICT_U8)

    sub_dir = d / 'subtlex-ch'
    sub_dir.mkdir()
    (sub_dir / 'SUBTLEX-CH-CHR.csv').write_text(SUBTLEX_CHR)
    (sub_dir / 'SUBTLEX-CH-WF.csv').write_text(SUBTLEX_WF)
    (sub_dir / 'SUBTLEX_CH_131210_CE.utf8').write_text(SUBTLEX_POS)

    rmw_dir = d / 'renminwang'
    rmw_dir.mkdir()
    (rmw_dir / 'RENMINWANG-CHR').write_text(RMW_CHR)
    (rmw_dir / 'RENMINWANG-WF').write_text(RMW_WF)

    return d


@pytest.fixture()
def patched_constants(monkeypatch: pytest.MonkeyPatch, assets_dir: Path) -> Path:
    """Monkeypatch all module-level path constants to point at the tmp assets dir."""
    ad = str(assets_dir)

    patches = {
        # hsg.classes.heisig
        'hsg.classes.heisig.HEISIG_CSV': os.path.join(ad, 'heisig.tsv'),
        # hsg.classes.hsk
        'hsg.classes.hsk.HSK_NEW_CSV': os.path.join(ad, 'hsk_new.csv'),
        'hsg.classes.hsk.HSK_OLD_CSV': os.path.join(ad, 'hsk_old.csv'),
        # hsg.classes.subtlexch
        'hsg.classes.subtlexch.SUBTLEX_CH_CHARS_CSV': os.path.join(ad, 'subtlex-ch', 'SUBTLEX-CH-CHR.csv'),
        'hsg.classes.subtlexch.SUBTLEX_CH_WORDS_CSV': os.path.join(ad, 'subtlex-ch', 'SUBTLEX-CH-WF.csv'),
        'hsg.classes.subtlexch.SUBTLEX_CH_WORDS_POS_COMBINED_CSV': os.path.join(
            ad, 'subtlex-ch', 'SUBTLEX_CH_131210_CE.utf8'
        ),
        # hsg.classes.renminwang
        'hsg.classes.renminwang.RMW_FREQUENCIES_CHARS_CSV': os.path.join(ad, 'renminwang', 'RENMINWANG-CHR'),
        'hsg.classes.renminwang.RMW_FREQUENCIES_WORDS_CSV': os.path.join(ad, 'renminwang', 'RENMINWANG-WF'),
        # hsg.classes.ccedict (ASSETS_DIR_PATH used for pickle path)
        'hsg.classes.ccedict.ASSETS_DIR_PATH': ad,
        # hsg.commands.heisigtatoeba
        'hsg.commands.heisigtatoeba.TATOEBA_CSV': os.path.join(ad, 'tatoeba.tsv'),
        # hsg.commands.ccedictsearch
        'hsg.commands.ccedictsearch.CCEDICT_CSV': os.path.join(ad, 'cedict_ts.u8'),
    }

    for target, value in patches.items():
        monkeypatch.setattr(target, value)

    # Remove any stale pickle so ccedict builds from the fixture
    pickle_path = os.path.join(ad, 'ccedict.pickle')
    if os.path.exists(pickle_path):
        os.remove(pickle_path)

    return assets_dir


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def app() -> click.Group:
    return cli
