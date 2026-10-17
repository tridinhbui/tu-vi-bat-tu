"""Before/after for a year reading. BEFORE = production /api/year (tiểu hạn + lưu Tứ Hóa advice; unchanged by Phase 2).
AFTER = same call with `experimental: true` (draft): how bản mệnh / đại hạn / lưu niên STACK on each palace + draft interaction rules.
Usage: python tools/compare_year_before_after.py 1990-5-17-10-30-male 2024 [more year args...]"""
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "engine")
from fastapi.testclient import TestClient  # noqa: E402

from tvbt.api import app  # noqa: E402

c = TestClient(app)
y_, m, d, h, mi, g = sys.argv[1].split("-")
for year in sys.argv[2:]:
    b = dict(year=int(y_), month=int(m), day=int(d), hour=int(h), minute=int(mi), gender=g, to_year=int(year))
    plain = c.post("/api/year", json=b).json()["tuvi"]
    x = c.post("/api/year", json={**b, "experimental": True}).json()["experimental"]
    print(f"### {sys.argv[1]} xem năm {year} (tuổi mụ {plain['age_tuoi_mu']})\n")
    print(f"**TRƯỚC (production)**: đại hạn {plain['dai_han']['palace']} ({plain['dai_han']['age_from']}–{plain['dai_han']['age_to']}); tiểu hạn ở {plain['tieu_han_palace']}; "
          f"lưu Thái Tuế ở {plain['luu_thai_tue_palace']}; lưu Tứ Hóa: " + "; ".join(f"{r['hoa']} ({r['star']}) ở {r['palace']}" for r in plain["luu_tu_hoa_reading"]) + ".")
    print(f"- {len(plain['tieu_han_reading'])} câu về tiểu hạn; mỗi tầng được đọc riêng, không có chỗ nào nói các tầng chồng lên nhau.\n")
    print("**SAU (đa tầng, thử nghiệm)**:\n")
    print(f"- đại hạn Tứ Hóa (can {x['layers']['dai_han_stem']}): " + "; ".join(f"{k} → {v}" for k, v in x["layers"]["dai_han_hoa"].items()))
    for pal, st in x["stack_by_palace"].items():
        if len(st["ky_layers"]) + len(st["loc_layers"]) >= 2 or len(st["layers"]) >= 2:
            print(f"- cung {pal}: các tầng cùng rơi vào đây — vị trí thời gian {st['layers'] or '—'}, hóa bản mệnh {st['natal_hoa'] or '—'}, đại hạn {st['dai_han_hoa'] or '—'}, lưu {st['luu_hoa'] or '—'}")
    for f in x["findings"]:
        print(f"- `{f['claim']}` ({f['effect']}, độ sâu {f['depth']}, {f['status']}) @{f['subject'][7:]}")
    for bl in x["blocked"]:
        print(f"- bị chặn bởi ngoại lệ: {bl['rule']} @ {bl['subject']}")
    for cf in x["conflicts"]:
        print(f"- mâu thuẫn khai báo: {cf['claim']} → {cf['status']}")
    print()
