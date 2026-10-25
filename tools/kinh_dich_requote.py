"""Re-anchor the quotes of dien_giai/<n>.json to the transcribed book text: a quote written against another copy of Ngô Tất Tố (Wikisource)
that is no longer found verbatim is replaced by the closest passage of the same segment and layer, only when the two agree on at least
90% of their characters. Anything further apart is listed, not changed.

  cd engine && ../.venv/bin/python ../tools/kinh_dich_requote.py 1 2 3 ... [--write]
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from tvbt.kinh_dich import dien_giai  # noqa: E402
from tvbt.kinh_dich.texts import DATA, quẻ_texts  # noqa: E402

MIN = 0.90


def norm(s):
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"')).strip()


def closest(quote: str, text: str) -> tuple[float, str]:
    """Best window of `text` (same number of words as the quote, ±3) by character ratio."""
    words = text.split(" ")
    n = len(quote.split(" "))
    best = (0.0, "")
    for size in range(max(1, n - 3), n + 4):
        for i in range(0, max(1, len(words) - size + 1)):
            cand = " ".join(words[i:i + size])
            r = SequenceMatcher(None, quote, cand, autojunk=False).ratio()
            if r > best[0]:
                best = (r, cand)
    return best


def fix(n: int, write: bool) -> list[str]:
    f = DATA / "dien_giai" / f"{n}.json"
    d = json.loads(f.read_text("utf-8"))
    segs = quẻ_texts(n)["segments"]
    report = []

    def visit(ref, where):
        layer = norm(segs.get(ref["seg"], {}).get("layers", {}).get(ref["layer"], ""))
        q = norm(ref["quote"])
        if q in layer:
            return
        r, cand = closest(q, layer)
        if r >= MIN:
            report.append(f"{n} {where}: {r:.2f} «{q[:50]}» -> «{cand[:50]}»")
            ref["quote"] = cand.rstrip(",;")
        else:
            report.append(f"{n} {where}: NO MATCH ({r:.2f}) «{q[:60]}»")

    for where, ref in dien_giai.quotes(d):
        visit(ref, where)
    if write:
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return report


if __name__ == "__main__":
    write = "--write" in sys.argv
    for a in [x for x in sys.argv[1:] if x.isdigit()]:
        for line in fix(int(a), write):
            print(line)
