"""Prints a before/after comparison of the reading for given births (markdown to stdout).
BEFORE = what production gives today for cách cục (analysis chapter 'cach-cuc' + number of production findings; byte-identical to pre-Phase-1,
see tools/ab_regression.py).  AFTER = the same chart through the Phase-1 engine with the EXPERIMENTAL formations (opt-in, draft).
Usage: python tools/compare_before_after.py 1950-1-4-4-10-male 1950-1-4-20-10-male ..."""
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "engine")
from fastapi.testclient import TestClient  # noqa: E402

from tvbt.api import app  # noqa: E402

c = TestClient(app)
for arg in sys.argv[1:]:
    y, m, d, h, mi, g = arg.split("-")
    b = dict(year=int(y), month=int(m), day=int(d), hour=int(h), minute=int(mi), gender=g)
    ana = c.post("/api/analysis", json=b).json()["chapters"]["cach-cuc"]
    rea = c.post("/api/reasoning", json={**b, "experimental": True}).json()
    ch = c.post("/api/chart", json=b).json()["tuvi"]
    menh = next(p for p in ch["palaces"] if p["name"] == "Mệnh")
    print(f"### Lá số {y}-{m}-{d} {h}:{mi} {g} — Mệnh {menh['stem']} {menh['branch']}, chính tinh: {', '.join(menh['major_stars']) or 'vô chính diệu'}\n")
    print("**TRƯỚC (production, không đổi)** — chương “Cách cục”:\n")
    for blk in ana[:3]:
        print(f"- [{blk['layer']}] {blk['text']}")
    print(f"\n  (production có {len(rea['systems']['tu_vi']['findings'])} nhận định Tử Vi; không có trạng thái thành/phá/cứu cho bất kỳ cách nào.)\n")
    print("**SAU (engine Phase 1, thử nghiệm, bật `experimental`)**:\n")
    shown = [f for f in rea["experimental"]["formations"] if f["state"] not in ("khong_hien",)]
    for f in shown:
        print(f"- `{f['id']}` → **{f['state']}** — {f['text']}")
    for f in rea["experimental"]["findings"]:
        if f["claim"].startswith("xr_"):
            print(f"- suy luận nhiều bước: `{f['claim']}` ({f['effect']}, độ sâu {f['depth']}, {f['status']}) ← " + " ← ".join(f["why"]["chain_vi"][:4]))
    for cf in rea["experimental"]["conflicts"]:
        print(f"- mâu thuẫn khai báo: {cf['claim']} → {cf['status']}")
    for bl in rea["experimental"]["blocked"]:
        print(f"- luật bị chặn bởi ngoại lệ: {bl['rule']} @ {bl['subject']}")
    print()
