"""Hand-transcribed reference charts (tests/reference_charts) must match the engine palace by palace, except the gaps a fixture declares
(cells the project's sources do not print). See tools/compare_reference.py."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from compare_reference import DEFAULT_DIR, compare  # noqa: E402

FILES = sorted(DEFAULT_DIR.glob("*.json"))


@pytest.mark.parametrize("path", FILES, ids=[f.stem for f in FILES])
def test_reference_chart(path):
    gaps = set(json.loads(path.read_text()).get("known_gaps", []))
    assert [d for d in compare(path) if d not in gaps] == []
