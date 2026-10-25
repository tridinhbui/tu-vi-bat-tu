"""Quality audit of the Kinh Dịch interpretation layer and readings (plan P5): writes docs/audit/KINH-DICH-EVAL.md and exits non-zero when a
gate fails.

  Coverage     every quẻ has Ngô Tất Tố's text for all segments and an interpretation file that passes its lint
  Distinct     the same field of two quẻ (core, a topic, advice…) never says the same thing: trigram Jaccard after masking the names of quẻ,
               quái and hào stays under 0.45 for every pair, and no sentence opening (first four words) is used by more than 6 quẻ
  Generic      a statement that would fit any quẻ: its masked trigrams are found in more than a quarter of the other quẻ's same field
  Length       the quick reading of a one-moving-line cast, with a topic, has at least 180 words; no own sentence over 60 words

  cd engine && ../.venv/bin/python ../tools/kinh_dich_eval.py [--out ../docs/audit/KINH-DICH-EVAL.md]
"""
from __future__ import annotations

import itertools
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.ha_lac import HEXAGRAMS  # noqa: E402
from tvbt.kinh_dich import core, dien_giai, doc_hao, reading  # noqa: E402
from tvbt.kinh_dich.texts import quẻ_texts  # noqa: E402

NAMES = sorted({h[0] for h in HEXAGRAMS.values()} | {"Kiền", "Khôn", "Chấn", "Tốn", "Khảm", "Ly", "Cấn", "Đoài", "Càn", "Đoái"}, key=len, reverse=True)
POS = r"(Chín|Sáu) (Đầu|Hai|Ba|Tư|Năm|Trên)"
# segments the printed book gives no dịch nghĩa for (transcription: 'absent', checked on the page image)
PRINTED_WITHOUT = {(28, "tieu_tuong5")}
J_MAX, OPEN_MAX, GENERIC_SHARE, QUICK_MIN, SENT_MAX = 0.45, 6, 0.25, 180, 60


def mask(t: str) -> str:
    t = re.sub(POS, "HAO", t)
    for n in NAMES:
        t = re.sub(rf"\b{re.escape(n)}\b", "QUE", t)
    return re.sub(r"\s+", " ", t.lower()).strip()


def grams(t: str) -> set:
    w = re.findall(r"\w+", mask(t))
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def jac(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def fields(d: dict) -> dict:
    out = {}
    for where, s in dien_giai.statements(d):
        key = re.sub(r"^hao\.\d\.", "hao.", where)       # the gist of hào 3 of one quẻ is compared with the gists of other quẻ
        out.setdefault(key, []).append(s["text"])
    return out


def main(out_path: Path | None) -> int:
    rows, fails = [], []
    by_field: dict[str, dict[int, list[str]]] = defaultdict(dict)
    openings: dict[str, set] = defaultdict(set)
    for n in range(1, 65):
        t = quẻ_texts(n)
        d = dien_giai.load(n)
        segs_missing = [k for k, s in t["segments"].items() if not s["layers"].get("nghia") and k != "intro" and (n, k) not in PRINTED_WITHOUT]
        bad = dien_giai.lint(n) if d and t["has_ntt"] else (["no interpretation"] if not d else ["no translation"])
        rows.append((n, HEXAGRAMS[n][0], t["has_ntt"], len(segs_missing), bool(d), len(bad)))
        if segs_missing or bad:
            fails.append(f"quẻ {n} {HEXAGRAMS[n][0]}: {len(segs_missing)} segments without dịch nghĩa; lint {bad[:3]}")
        if d:
            for k, texts in fields(d).items():
                by_field[k][n] = texts
                if k == "hao.position":            # 'Hào dương ở ngôi…' is the same frame by nature: not an opening to vary
                    continue
                for x in texts:
                    openings[" ".join(mask(x).split()[:4])].add(n)
    worst, generic = [], []
    for k, per in by_field.items():
        gs = {n: set().union(*(grams(x) for x in xs)) for n, xs in per.items()}
        for a, b in itertools.combinations(sorted(gs), 2):
            j = jac(gs[a], gs[b])
            if j >= J_MAX:
                worst.append((j, k, a, b))
        if k == "hao.position":                # positions are facts of the same kind in every quẻ, not advice that fits any quẻ
            continue
        for n, xs in per.items():
            for x in xs:
                g = grams(x)
                hits = sum(1 for m, h in gs.items() if m != n and len(g & h) >= max(3, len(g) // 2))
                if len(gs) > 4 and hits > GENERIC_SHARE * (len(gs) - 1):
                    generic.append((k, n, x))
    over = [(o, sorted(ns)) for o, ns in openings.items() if len(ns) > OPEN_MAX]
    short, long_s = [], []
    for n in range(1, 65):
        if not dien_giai.load(n):
            continue
        c = core.from_hexagram(n, [3])
        c["reading_rule"] = doc_hao.resolve(c)
        r = reading.read(c, "su_nghiep")
        quick = [s for sec in r["sections"] for p in sec["paragraphs"] if p["depth"] != "sau" for s in p["sentences"]]
        words = sum(len(s["text"].split()) for s in quick)
        if words < QUICK_MIN:
            short.append((n, words))
        long_s += [(n, s["text"][:60]) for s in quick if s["basis"] in ("dien_giai", "loi_khuyen") and len(s["text"].split()) > SENT_MAX]
    fails += [f"similar {k}: quẻ {a} / {b} J={j:.2f}" for j, k, a, b in sorted(worst, reverse=True)]
    fails += [f"opening '{o}' in {len(ns)} quẻ {ns}" for o, ns in over]
    fails += [f"generic {k} quẻ {n}: {x[:70]}" for k, n, x in generic]
    fails += [f"quick reading of quẻ {n} has {w} words" for n, w in short]
    fails += [f"long sentence quẻ {n}: {x}" for n, x in long_s]
    lines = ["# Kinh Dịch: kiểm tra chất lượng phần diễn giải", "",
             f"Ngưỡng: Jaccard < {J_MAX}, một mở đầu câu ≤ {OPEN_MAX} quẻ, câu chung chung ≤ {GENERIC_SHARE:.0%} số quẻ, đọc nhanh ≥ {QUICK_MIN} chữ, "
             f"câu của hệ thống ≤ {SENT_MAX} chữ.", "",
             "| Quẻ | Tên | Bản dịch | Đoạn thiếu dịch nghĩa | Diễn giải | Lỗi lint |", "|---|---|---|---|---|---|"]
    lines += [f"| {n} | {name} | {'có' if t else 'chưa'} | {m} | {'có' if d else 'chưa'} | {b} |" for n, name, t, m, d, b in rows]
    lines += ["", f"## Kết quả: {'ĐẠT' if not fails else f'{len(fails)} chỗ chưa đạt'}", ""] + [f"- {f}" for f in fails[:300]]
    text = "\n".join(lines) + "\n"
    if out_path:
        out_path.write_text(text, "utf-8")
    print(text if len(text) < 6000 else text[-6000:])
    return 1 if fails else 0


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    sys.exit(main(out))
