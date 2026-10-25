"""Print a quẻ's texts segment by segment (Hán, dịch nghĩa, Trình Di, Chu Hy, tiên nho) for writing or checking dien_giai/<n>.json.

  cd engine && TVBT_KD_NTT_DIR=<ntt dir> ../.venv/bin/python ../tools/kinh_dich_show.py 7 [--lint]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from tvbt.kinh_dich.dien_giai import lint  # noqa: E402
from tvbt.kinh_dich.texts import quẻ_texts  # noqa: E402

n = int(sys.argv[1])
if "--lint" in sys.argv:
    bad = lint(n)
    print("\n".join(bad) or "ok")
    sys.exit(1 if bad else 0)
t = quẻ_texts(n)
print(f"# Quẻ {n} {t['han']}  (bản dịch: {'có' if t['has_ntt'] else 'CHƯA CÓ'}; không khớp: {t['unmatched']})")
for k, s in t["segments"].items():
    print(f"\n## {k}  {s['han']}")
    for layer in ("nghia", "trinh_di", "chu_hy", "tien_nho"):
        v = s["layers"].get(layer)
        if v:
            print(f"[{layer}] {v}")
