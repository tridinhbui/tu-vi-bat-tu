"""Hand-transcribed reference charts (tests/reference_charts) must match the engine palace by palace, natal Tứ Hóa and the board's lưu
Tứ Hóa included, except the gaps a fixture declares (cells the project's sources do not print, school differences such as the board's
Canh row). See tools/compare_reference.py."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from compare_reference import DEFAULT_DIR, compare, hoa_info  # noqa: E402

FILES = sorted(DEFAULT_DIR.glob("*.json"))


def test_fixtures_present():
    assert {f.stem for f in FILES} >= {"1911-01-01_1230_nam", "1971-05-24_1030_nam", "2002-01-09_0430_nam"}


@pytest.mark.parametrize("path", FILES, ids=[f.stem for f in FILES])
def test_reference_chart(path):
    gaps = set(json.loads(path.read_text()).get("known_gaps", []))
    assert [d for d in compare(path) if d not in gaps] == []


@pytest.mark.parametrize("path", FILES, ids=[f.stem for f in FILES])
def test_known_gaps_still_occur(path):
    """A declared gap that no longer shows up means the engine (or its default) changed: update the fixture, do not keep stale gaps."""
    gaps = set(json.loads(path.read_text()).get("known_gaps", []))
    assert gaps - set(compare(path)) == set()


@pytest.mark.parametrize("path", [f for f in FILES if json.loads(f.read_text()).get("hoa")],
                         ids=[f.stem for f in FILES if json.loads(f.read_text()).get("hoa")])
def test_board_hoa_matches_some_table(path):
    """Every transcribed Hóa row (natal and each lưu year) is a row of at least one Tứ Hóa table the engine ships, so a mismatch with
    the default table is a school difference, not a transcription slip."""
    assert [x for x in hoa_info(path) if x.endswith("không bảng nào")] == []
