"""Quality metrics of the Western reading over many charts (no language model involved).

Corpus: N charts drawn with a fixed seed: births 1900-2100, nine cities on both hemispheres plus a polar one (Placidus falls
back to Porphyry there), one chart in ten without a birth time. Reading date 25/10/2026.

  audit        issue counts from western.reading.audit over the corpus
  per chapter  paragraphs and sentences per reading, words in the Đọc nhanh view, the share of sentences that are still
               identical across >= 50% of the charts after chart words (planets, signs, numbers) are blanked ('strip'),
               and the share of sentences that carry a chart datum ('data': a degree, a sign, a planet, a house)
  summaries    for each life chapter: how often it has its summary, how its thesis and verdict spread over the corpus
               (a thesis that is the same for 90% of charts says nothing), how many claims and evidence chips it rests on
  consistency  the same planet called 'đắc thế' and 'thất thế' in Lilly's paragraphs of one reading (a contradiction)
  glossary     in the Đọc nhanh view, how many technical words have a glossary entry (linked on the page)
  critical     birth time moved by 2 hours: share of natal paragraphs whose text changes (should be high)
  inert        longitude moved by 0.001 degree: share whose text changes (should be ~0)

    python tools/west/eval_reading.py [N] [--report docs/WESTERN-EVAL.md]
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import random
import re
import statistics
import sys
import time

sys.path.insert(0, "engine")
from western.chart import BirthData, compute  # noqa: E402
from western.reading import build  # noqa: E402
from western.reading.argue import SUMMARIES  # noqa: E402
from western.reading.audit import sentences  # noqa: E402
from western.reading.vocab import PLANET_VI, SIGN_VI  # noqa: E402

WHEN = dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc)
CITIES = [(10.8231, 106.6297, "Asia/Ho_Chi_Minh"), (21.0285, 105.8542, "Asia/Hanoi"), (48.8566, 2.3522, "Europe/Paris"),
          (40.7128, -74.006, "America/New_York"), (35.6762, 139.6503, "Asia/Tokyo"), (-33.8688, 151.2093, "Australia/Sydney"),
          (51.5072, -0.1276, "Europe/London"), (-23.5505, -46.6333, "America/Sao_Paulo"), (55.7558, 37.6173, "Europe/Moscow"),
          (69.6492, 18.9553, "Europe/Oslo")]
WORDS = sorted(list(PLANET_VI.values()) + list(SIGN_VI.values()), key=len, reverse=True)
DATA = re.compile(r"\d+°|Nhà \d+|" + "|".join(re.escape(w) for w in WORDS))
TECH = ["phẩm vị", "đắc thế", "thất thế", "chủ tinh", "nhà góc", "nhà suy", "nghịch hành", "góc hài hòa", "góc căng", "cát tinh", "hung tinh",
        "cung Mọc", "Thiên Đỉnh", "Lot of Fortune", "Part of Fortune", "profection", "transit", "tiến trình", "Solar Return", "khí chất",
        "lạc chỗ", "nhóm nguyên tố", "định tinh", "trọn cung", "cách chia của Lilly", "Daimon", "chủ năm", "chủ lá số"]
STATE = re.compile(r"(Mặt Trời|Mặt Trăng|Sao Thủy|Sao Kim|Sao Hỏa|Sao Mộc|Sao Thổ)[^.;:()]{0,30}?(đắc thế|thất thế)")


def strip(s: str) -> str:
    for w in WORDS:
        s = s.replace(w, "X")
    return re.sub(r"\d+([.,]\d+)?", "N", s)


def natal_texts(r: dict) -> dict:
    return {p["id"]: p["text"] for ch in r["chapters"] if ch["id"] != "thoi_van" for p in ch["paragraphs"]}


def corpus(n: int) -> list[BirthData]:
    rnd = random.Random(42)
    out = []
    while len(out) < n:
        lat, lon, tz = rnd.choice(CITIES)
        y, m, d = rnd.randint(1900, 2100), rnd.randint(1, 12), rnd.randint(1, 28)
        if rnd.random() < 0.1:
            out.append(BirthData(y, m, d, None, None, lat, lon, tz))
        else:
            out.append(BirthData(y, m, d, rnd.randint(0, 23), rnd.randint(0, 59), lat, lon, tz))
    return out


def main(n: int, report: str | None):
    charts = corpus(n)
    rnd = random.Random(7)
    t0 = time.time()
    audits = collections.Counter()
    sent_counter = collections.Counter()
    ch_sent = collections.defaultdict(list)
    ch_paras = collections.defaultdict(list)
    ch_quick_words = collections.defaultdict(list)
    ch_data = collections.defaultdict(lambda: [0, 0])
    ch_strip = collections.defaultdict(collections.Counter)
    thesis = collections.defaultdict(collections.Counter)
    verdict = collections.defaultdict(collections.Counter)
    sum_claims = collections.defaultdict(list)
    sum_ev = collections.defaultdict(list)
    sum_present = collections.Counter()
    sum_expected = collections.Counter()
    contradictions = []
    tech_seen = collections.Counter()
    crit, inert, failed = [], [], 0
    gl = json.loads(pathlib.Path("engine/web/js/glossary.json").read_text("utf-8")).get("west_aliases", {})
    n_ok = 0
    for i, b in enumerate(charts):
        try:
            c = compute(b)
            r = build(c, "deep", rnd.choice([None, "male", "female"]), WHEN)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAILED", b, e, file=sys.stderr)
            continue
        n_ok += 1
        audits.update(r["audit"]["counts"])
        states = collections.defaultdict(set)
        for ch in r["chapters"]:
            cid = ch["id"]
            ps = ch["paragraphs"]
            ch_paras[cid].append(len(ps))
            quick = [p for p in ps if p.get("layer") == "summary"] or [p for p in ps if p["level"] != "deep"]
            ch_quick_words[cid].append(sum(len(p["text"].split()) for p in quick))
            ns = 0
            seen = set()
            for p in ps:
                for s in sentences(p["text"]):
                    ns += 1
                    ch_data[cid][0] += 1
                    ch_data[cid][1] += bool(DATA.search(s))
                    k = strip(s)
                    if k not in seen:
                        ch_strip[cid][k] += 1
                        sent_counter[k] += 1
                        seen.add(k)
                if p["school"] == "traditional":
                    for m in STATE.finditer(p["text"]):
                        states[m.group(1)].add(m.group(2))
            ch_sent[cid].append(ns)
            for p in quick:
                for t in TECH:
                    if t in p["text"]:
                        tech_seen[t] += 1
            if cid in SUMMARIES:
                expected = b.hour is not None or cid in ("tinh_cach", "tu_duy", "cam_xuc")
                sum_expected[cid] += expected
                sm = [p for p in ps if p.get("layer") == "summary"]
                if sm:
                    sum_present[cid] += 1
                    keys = dict(k.split(":", 1) for k in sm[0]["keys"] if ":" in k)
                    thesis[cid][keys.get("thesis", "?")] += 1
                    verdict[cid][keys.get("verdict", "?")] += 1
                    sum_claims[cid].append(len(sm[0]["steps"]) - 1)
                    sum_ev[cid].append(len(sm[0]["evidence"]))
        bad = [p for p, st in states.items() if len(st) > 1]
        if bad:
            contradictions.append((i, bad))
        if i < 40 and b.hour is not None:
            texts = natal_texts(r)
            b2 = BirthData(b.year, b.month, b.day, (b.hour + 2) % 24, b.minute, b.lat, b.lon, b.tz)
            b3 = BirthData(b.year, b.month, b.day, b.hour, b.minute, b.lat, b.lon + 0.001, b.tz)
            for bb, acc in ((b2, crit), (b3, inert)):
                try:
                    t2 = natal_texts(build(compute(bb), "deep", r["gender"], WHEN))
                except Exception:  # noqa: BLE001
                    continue
                common = set(texts) & set(t2)
                acc.append(sum(texts[k] != t2[k] for k in common) / max(1, len(common)))
    N = n_ok
    lines = [f"# Đánh giá luận giải Chiêm tinh trên {N} lá số", "",
             f"Sinh bằng `python tools/west/eval_reading.py {n}` ngày {dt.date.today():%d/%m/%Y}, {time.time() - t0:.0f} giây; {failed} lá lỗi.", "",
             f"Audit: {dict(audits) or 'không có lỗi'}", "",
             "## Theo chương", "", "| Chương | đoạn | câu | chữ ở Đọc nhanh | câu có dữ kiện lá số | câu giống ở ≥50% lá |", "|---|---|---|---|---|---|"]
    for cid in ch_paras:
        st = ch_strip[cid]
        tot = sum(st.values())
        boiler = sum(v for v in st.values() if v >= N * 0.5)
        lines.append(f"| {cid} | {statistics.mean(ch_paras[cid]):.1f} | {statistics.mean(ch_sent[cid]):.1f} | {statistics.mean(ch_quick_words[cid]):.0f} | "
                     f"{ch_data[cid][1] / max(1, ch_data[cid][0]):.0%} | {boiler / max(1, tot):.0%} |")
    lines += ["", "## Phần tóm tắt của tám chương", "", "| Chương | có tóm tắt | luận điểm phổ biến nhất | phân bố kết luận | chứng TB | chip TB |", "|---|---|---|---|---|---|"]
    for cid in SUMMARIES:
        th = thesis[cid]
        top, topn = (th.most_common(1)[0] if th else ("?", 0))
        lines.append(f"| {cid} | {sum_present[cid]}/{sum_expected[cid]} | {top} ({topn / max(1, sum(th.values())):.0%}) | "
                     + ", ".join(f"{k} {v / max(1, sum(verdict[cid].values())):.0%}" for k, v in verdict[cid].most_common()) + " | "
                     f"{statistics.mean(sum_claims[cid] or [0]):.1f} | {statistics.mean(sum_ev[cid] or [0]):.1f} |")
    lines += ["", f"Mâu thuẫn đắc thế / thất thế trong các đoạn của Lilly: {len(contradictions)} lá" + (f" (ví dụ lá {contradictions[0]})" if contradictions else ""), ""]
    lines += ["Thuật ngữ trong Đọc nhanh: " + ", ".join(f"{t} {v}" + ("" if t in gl else " (CHƯA có mục glossary)") for t, v in tech_seen.most_common()), ""]
    if crit:
        lines.append(f"Đổi giờ sinh 2 tiếng: {statistics.mean(crit):.0%} đoạn của lá gốc đổi chữ (nên cao).")
    if inert:
        lines.append(f"Dời kinh độ 0,001°: {statistics.mean(inert):.1%} đoạn đổi (nên gần 0).")
    lines += ["", "## Câu lặp nhiều nhất (sau khi thay tên sao, cung, số bằng X/N)", ""]
    for s, v in sent_counter.most_common(15):
        lines.append(f"- {v / N:.0%} · {s[:160]}")
    out = "\n".join(lines) + "\n"
    print(out)
    if report:
        pathlib.Path(report).write_text(out, "utf-8")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rep = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    if rep in args:
        args.remove(rep)
    main(int(args[0]) if args else 60, rep)
