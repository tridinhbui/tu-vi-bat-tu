// The chart as plain Vietnamese text for the model: computed facts, then the deterministic reading chapter by chapter.
// The model is told to answer only from this text, so everything it may say about the chart has to be here.
import { interpretAll } from "../interpret/pipeline.ts";
import type { ChartInput, Knowledge } from "../interpret/types.ts";

const join = (a: unknown[]) => a.filter(Boolean).join(", ");

export function chartFacts(c: ChartInput): string {
  const L: string[] = [];
  L.push(`Năm sinh dương lịch ${c.birth_year}, âm lịch ${c.lunar_year} (${c.year_gz}). Giới tính: ${c.gender === "male" ? "nam" : "nữ"} (${c.yin_yang_gender}).`);
  L.push(`${c.cuc.name}; Mệnh nạp âm ${c.menh_nap_am}; quan hệ Cục–Mệnh: ${c.menh_cuc_relation}. Đại hạn đi ${c.dai_han_direction}.`);
  L.push("", "MƯỜI HAI CUNG:");
  for (const p of c.palaces) {
    const dig = (s: string) => { const d = p.major_dignity?.[s] ?? p.minor_dignity?.[s]; return d ? `${s} (${d})` : s; };
    const major = p.major_stars.map(dig), minor = p.stars.filter(s => !p.major_stars.includes(s)).map(dig);
    L.push(`- ${p.name}${p.is_than ? " (cũng là cung Thân)" : ""} · ${p.stem} ${p.branch}: chính tinh ${major.length ? join(major) : "không có"}; phụ tinh ${minor.length ? join(minor) : "không có"}${p.tuan ? "; Tuần" : ""}${p.triet ? "; Triệt" : ""}`);
  }
  const hoa = Object.entries(c.tu_hoa ?? {});
  if (hoa.length) L.push("", `TỨ HÓA NĂM SINH: ${join(hoa.map(([k, v]) => `${k} ${v.star}`))}`);
  if (c.decades?.length) {
    L.push("", "ĐẠI HẠN:");
    for (const d of c.decades) L.push(`- ${d.age_from}–${d.age_to} tuổi: cung ${d.palace} (${d.stem} ${d.branch})`);
  }
  if (c.year) {
    const y = c.year;
    L.push("", `NĂM ĐANG XEM ${y.year} (${y.age_tuoi_mu} tuổi mụ)${y.annual_pillar ? `, năm ${y.annual_pillar}` : ""}: ` +
      `${y.dai_han ? `đại hạn cung ${y.dai_han.palace} (${y.dai_han.age_from}–${y.dai_han.age_to}); ` : ""}${y.tieu_han_palace ? `tiểu hạn tại cung ${y.tieu_han_palace}` : ""}${y.tieu_han_topic ? `, chủ đề ${y.tieu_han_topic}` : ""}.`);
  }
  if (c.bazi) {
    const b = c.bazi, name = { year: "Năm", month: "Tháng", day: "Ngày", hour: "Giờ" } as const;
    L.push("", "BÁT TỰ:");
    for (const k of ["year", "month", "day", "hour"] as const) {
      const p = b.pillars[k]; if (!p) continue;
      L.push(`- Trụ ${name[k]}: ${p.stem} ${p.branch}${p.stem_ten_god ? `, thập thần ${p.stem_ten_god}` : ""}${p.stage ? `, ${p.stage}` : ""}${p.hidden?.length ? `; tàng can ${join(p.hidden.map(h => `${h.stem} (${h.ten_god})`))}` : ""}`);
    }
    L.push(`Nhật chủ ${b.day_master} (${b.day_master_element}). Đại vận đi ${b.luck_direction}, khởi vận lúc ${b.luck_start_age} tuổi: ${join(b.luck.map(l => `${l.name} từ ${l.start_age} tuổi${l.ten_god ? ` (${l.ten_god})` : ""}`))}.`);
  }
  return L.join("\n");
}

export function buildContext(chart: ChartInput, k: Knowledge): string {
  const chapters = interpretAll(chart, k).map(o => `## ${o.title}\n${o.text}`).join("\n\n");
  return `DỮ KIỆN LÁ SỐ (do máy tính, không phải diễn giải)\n${chartFacts(chart)}\n\nBÀI LUẬN GIẢI (đã đối chiếu sách, theo từng chương)\n${chapters}`;
}
