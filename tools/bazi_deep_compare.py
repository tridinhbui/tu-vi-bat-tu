"""Before/after on EX1-EX15: frozen pre-upgrade view (tests/golden/bazi_deep_baseline.json) vs bazi_deep. Writes docs/BAZI_DEEP_AB_REPORT.md.
EX charts have no birth instant, so tư lệnh is OFF here (days_into_month unknown); the report says so."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.bazi_deep import pipeline
from tvbt.bazi_deep.model import ChartView
from tvbt.bazi_deep import temporal_deep as td
from tvbt.bazi_deep.profile import DEFAULT

base = json.loads((ROOT / "engine/tests/golden/bazi_deep_baseline.json").read_text("utf-8"))
ex = json.loads((ROOT / "engine/data/bazi_deep/examples.json").read_text("utf-8"))["charts"]
rows, trows, tot = [], [], {"old_rel": 0, "new_int": 0, "changed": 0, "cach": 0, "amb": 0, "bai": 0, "hoa_not_none": 0, "dis": 0}
for k, t in ex.items():
    o = pipeline.analyse(ChartView.from_names(t))
    b = base[k]
    f = o["facts"]
    n_old = sum(len(v) for v in b["relations_old"].values())
    tot["old_rel"] += n_old; tot["new_int"] += len(o["interactions"])
    tot["changed"] += f["bazi.level_changed_by_interaction"]; tot["cach"] += bool(f["bazi.geju_inner"]); tot["amb"] += f["bazi.dm_ambiguous"]
    tot["bai"] += f["bazi.geju_state"] in ("bai", "bai_cuu_yeu"); tot["dis"] += bool(f["bazi.method_disagreements"])
    outer = ", ".join(f"{x['name']} ({x['quality']})" for x in o["geju"]["outer"]) or "—"
    inner = ", ".join(f"{x['name']} ({x['state']})" for x in o["geju"]["inner"]) or "—"
    nat = td.natal_bundle(ChartView.from_names(t)); eff = {}
    for n in range(60):
        e = td.analyse_extended(ChartView.from_names(t), DEFAULT, nat, [td.tp("luck", n % 10, n % 12)])["effect"]
        eff[e] = eff.get(e, 0) + 1
    pats = ", ".join(x.replace(":", " = ") for x in f["bazi.patterns"]) or "—"
    trows.append(f"| {k} | {eff.get('tro_cach', 0)} | {eff.get('pha_cach', 0)} | {eff.get('doi_cach', 0)} | {eff.get('trung_tinh', 0)} | {pats} |")
    rows.append(f"| {k} | {t} | {'có' if b['dac_lenh_old_boolean'] else 'không'} / căn: {len(b['root_pillars_old'])} trụ / {n_old} quan hệ cặp | "
                f"{o['strength_raw']['level']} → **{o['strength_after']['level']}**{' ⚠ sát ranh giới' if f['bazi.dm_ambiguous'] else ''} | "
                f"{o['strength_after']['axes']['de_lenh']}; căn {o['strength_after']['axes']['de_dia']} | {len(o['interactions'])} ({', '.join(sorted(set(i['status'] for i in o['interactions'] if i.get('status'))))}) | "
                f"{inner}; ngoại: {outer} | {f['bazi.hua_state']} | {len(o['reasoning']['findings'])} |")
out = ["# So sánh trước/sau trên EX1–EX15", "",
       "Sinh bởi `tools/bazi_deep_compare.py`. **Trước** = pipeline cũ đã đóng băng (`engine/tests/golden/bazi_deep_baseline.json`): đắc lệnh là boolean, căn là danh sách trụ, chỉ quan hệ từng cặp, không có cách cục/dụng thần.",
       "**Sau** = `tvbt.bazi_deep` với `SchoolProfile baseline_v1` (mọi trọng số, ngưỡng, bảng cách: **draft**, chưa đối chiếu sách). Lá số EX không có giờ sinh thực nên tư lệnh TẮT.", "",
       "| Mã | Tứ Trụ | Trước | Khí thế: nguyên cục → sau tương tác | Trục lệnh/địa (sau) | Tương tác (số, trạng thái) | Cách cục | Hợp can mạnh nhất | Số finding |",
       "|---|---|---|---|---|---|---|---|---|", *rows, "",
       "## Cục mở rộng: đặt thử cả 60 trụ Giáp Tý…Quý Hợi làm đại vận lên từng lá số", "",
       "Trước: chỉ có quan hệ từng cặp giữa trụ vận và nguyên cục, không tính lại cách. Sau: tính lại khí thế, cách cục, cấu trúc và dụng thần trên cục mở rộng (`temporal_deep`). Bảng đếm kết quả so với nguyên cục (draft).", "",
       "| Mã | Trợ cách | Phá cách | Đổi cách | Trung tính | Cấu trúc thập thần nguyên cục (draft) |", "|---|---|---|---|---|---|", *trows, "",
       "## Tổng hợp", "",
       f"- Quan hệ: cũ tìm {tot['old_rel']} quan hệ cặp trên 15 lá số; mới ghi {tot['new_int']} tương tác (có thêm bán hợp, củng hợp, bán hình, vị trí kề/cách vị, trạng thái đã giải).",
       f"- Tương tác làm đổi mức khí thế Nhật Chủ ở {tot['changed']}/15 lá số.",
       f"- Cách cục: cũ 0/15 lá số có nhãn; mới định được ứng viên ở {tot['cach']}/15; {tot['bai']} lá số có cách đang bại.",
       f"- Khí thế sát ranh giới (hệ thống không chọn một mức): {tot['amb']}/15.",
       f"- Các phương pháp dụng thần bất đồng ít nhất một nhóm thập thần: {tot['dis']}/15.", "",
       "Mọi số liệu trên là kết quả của quy tắc hệ thống đang ở trạng thái draft; chúng cho thấy hệ thống đã làm gì khác trước, không chứng minh kết luận mệnh lý đúng."]
dst = ROOT / "docs/BAZI_DEEP_AB_REPORT.md"
dst.write_text("\n".join(out) + "\n", "utf-8")
print("wrote", dst); print("\n".join(out[-9:]))
