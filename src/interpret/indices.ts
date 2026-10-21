// System indices for the overview charts (docs/PRODUCT-PLAN.md phase 1.1–1.4): "Mức thuận lợi" / "Mức thử thách" per đại hạn, per year,
// per palace and per month. An index is NOT a probability or a forecast: it is a weighted count of the book readings that fire on a palace
// and its tam phương, split by the side the reading takes (support / limit), and every value lists the items it sums.
//
// Layers (each item says which one it belongs to):
//   ban_menh      verified natal findings of the rule engine (engine.ts) on the palace (self), its opposite and its two tam hợp palaces.
//                 weight = TIER_WEIGHT[tier of the finding's seat, read with its own palace as centre] × (0.5 + rarity) × SCOPE_WEIGHT[scope]
//                 (reason/tiers.ts: the reasoner's own weights). The same claim on the same palace counts once. A rule the R1 position guard
//                 rejects does not count. The books write about Mệnh far more than about any other palace, so a raw sum would make every
//                 chart peak wherever Mệnh's findings land; the layer is therefore told as a RATIO to the mean of the same palace over the
//                 1,000-chart corpus (engine/data/kg/index_norms.json, tools/interpret/index_norms.ts), smoothed by one plain finding:
//                 (sum + 1) / (mean + 1). 1 = as much as the corpus' typical chart has there (system convention, he_thong).
//   van           the vận-palace readings the Python engine already attaches to every palace (facts.decades): Khảo Luận pp.233-236 and Thực
//                 Hành pp.115-117 (van_han_rules.json, by rule id), Toàn Thư pp.97-105 nhập hạn ca (paraphrased, page check pending: weight
//                 ×0.6), Khảo Luận pp.230-233 (tam hợp of the vận against the birth year; the vận's tam hợp controlling the opposite's).
//                 The side of each reading is the side its book sentence states ("dịp đi lên" / "thế đi xuống", "hao tài" …), tabled below.
//   luu_thai_tue  (years only) half the ban_menh index of the palace the year's Thái Tuế stands in. Position: KL tr.41-42; the half weight
//                 is a system convention.
//   luu_tu_hoa    (years only) the Tứ Hóa of the year's stem landing in the tiểu hạn palace's tam phương, weight 0.3 × scope: a common
//                 convention the three books do not give (KL tr.41-42 and TH tr.114 list nine lưu stars, no Tứ Hóa), labelled so.
// Month (nguyệt hạn, TH tr.115): only the palace each month falls in is sourced, so a month carries that palace's ban_menh index alone.
import type { ChartInput, Knowledge, Palace, Rule } from './types.ts';
import { run } from './engine.ts';
import { triggerAtoms } from './kg/atoms.ts';
import type { World } from './dsl.ts';
import { Geo, SCOPE_WEIGHT, TIER_WEIGHT, atomSeat, rarity, type Tier } from './reason/tiers.ts';
import { guardHolds } from './reason/positions.ts';

export const INDICES_VERSION = 'indices-1.0.0';
export const DISCLAIMER = 'Chỉ số tổng hợp từ quy tắc sách, không phải xác suất hay dự báo.';

export type Side = 'support' | 'limit';
export type Layer = 'ban_menh' | 'van' | 'luu_thai_tue' | 'luu_tu_hoa';
/** sach: a book sentence with its page; sach_dien_giai: a paraphrased book passage whose page is still to be checked; thong_le: convention */
export type ItemBasis = 'sach' | 'sach_dien_giai' | 'thong_le';
export type Rel = 'self' | 'opp' | 'trine';
export interface Item { id: string; side: Side; w: number; layer: Layer; palace: string; scope: Rel; cite: string; text: string; basis: ItemBasis }

const r3 = (x: number) => Math.round(x * 1000) / 1000;
/** A number as Vietnamese text: decimal comma, two places ("3,3" not "3.297", which reads as three thousand). */
const vn = (x: number) => String(Math.round(x * 100) / 100).replace('.', ',');
const STEMS = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const REL_OF: Record<number, Rel> = { 0: 'self', 6: 'opp', 4: 'trine', 8: 'trine' };

// ---- the side of each vận reading, as its book sentence states it (weights: 1 plain, 0.5 when the sentence is conditional or mild) ----
/** Khảo Luận pp.233-236 / Thực Hành pp.115-117 (engine/data/van_han_rules.json) by rule id. */
export const VAN_RULES: Record<string, { side: Side; w: number }> = {
  VH_TPVT_SAT: { side: 'support', w: 1 }, VH_TPVT_CNDL: { side: 'limit', w: 1 }, VH_VCD_SPT: { side: 'support', w: 1 },
  VH_TUAN_TRIET: { side: 'support', w: 1 }, VH_NN_DAO_HONG: { side: 'support', w: 0.5 }, VH_NN_KINH_DA: { side: 'limit', w: 1 },
  VH_CU_NHAT_SPT: { side: 'support', w: 1 }, VH_CNDL_TOT: { side: 'support', w: 1 }, VH_CNDL_XAU: { side: 'limit', w: 1 },
  VH_VT_TP: { side: 'support', w: 1 }, VH_VT_SPT: { side: 'support', w: 1 }, VH_THAI_TUE: { side: 'support', w: 1 },
  VH_QUAN_PHU: { side: 'support', w: 0.5 }, VH_BACH_HO: { side: 'support', w: 0.5 },
  VH_POS_1: { side: 'support', w: 1 }, VH_POS_2: { side: 'limit', w: 1 }, VH_POS_3: { side: 'support', w: 1 }, VH_POS_4: { side: 'limit', w: 1 },
  VH_POS_5: { side: 'support', w: 1 }, VH_POS_6: { side: 'limit', w: 1 },
  TH_TPVT_LOC_TA_HUU: { side: 'support', w: 1 }, TH_NDCC_HOA3: { side: 'support', w: 1 }, TH_CU_NHAT_SONG_LOC: { side: 'support', w: 1 },
  TH_CNDL_TAM_HOA: { side: 'support', w: 1 }, TH_SPLT_KINH_DOANH: { side: 'support', w: 1 }, TH_DAO_HONG_KHOA_QUYEN: { side: 'support', w: 1 },
  TH_TPVT_KHONG_KIEP_KY: { side: 'limit', w: 1 }, TH_NDCC_KHONG_KIEP: { side: 'limit', w: 1 },
};
/** Toàn Thư pp.97-105 nhập hạn ca (engine/tvbt/van_han_tt.py): matched by the start of the sentence; the longer prefix is tried first. */
export const TT_SENTENCES: Array<{ id: string; prefix: string; side: Side; w: number }> = [
  ['TT_HAN_TU_VI_SPT', 'Tử Vi nhập hạn nhưng tam phương có Thất Sát', 'limit', 1], ['TT_HAN_TU_VI', 'Hạn đến Tử Vi ở thế đẹp', 'support', 1],
  ['TT_HAN_CO_HOA', 'Hạn Thiên Cơ gặp Khoa, Quyền hoặc Lộc', 'support', 1], ['TT_HAN_CO', 'Hạn Thiên Cơ:', 'limit', 1],
  ['TT_HAN_NHAT_DAC', 'Hạn Thái Dương đắc địa', 'support', 1], ['TT_HAN_NHAT_HAM', 'Hạn Thái Dương hãm địa', 'limit', 1],
  ['TT_HAN_VU_MIEU', 'Hạn Vũ Khúc nhập miếu', 'support', 1], ['TT_HAN_VU_QUYEN', 'Hạn Vũ Khúc có Hóa Quyền', 'support', 1],
  ['TT_HAN_VU_HAM', 'Hạn Vũ Khúc hãm địa', 'limit', 1], ['TT_HAN_DONG_DAC', 'Hạn Thiên Đồng đắc địa', 'support', 1],
  ['TT_HAN_DONG_HAM', 'Hạn Thiên Đồng hãm địa', 'limit', 1], ['TT_HAN_LIEM_VUONG', 'Hạn Liêm Trinh ở thế vượng', 'support', 1],
  ['TT_HAN_PHU', 'Hạn Thiên Phủ:', 'support', 1], ['TT_HAN_NGUYET_HAM', 'Hạn Thái Âm hãm địa', 'limit', 1], ['TT_HAN_NGUYET', 'Hạn Thái Âm:', 'support', 1],
  ['TT_HAN_THAM_MIEU', 'Hạn Tham Lang miếu vượng', 'support', 1], ['TT_HAN_THAM_HOA', 'Hạn Tham Lang ở Tứ mộ gặp Hỏa Tinh', 'support', 1],
  ['TT_HAN_THAM_HAM', 'Hạn Tham Lang hãm địa', 'limit', 1], ['TT_HAN_PHA_MIEU', 'Hạn Phá Quân miếu địa', 'support', 1],
  ['TT_HAN_PHA_SAT', 'Hạn Phá Quân gặp sát tinh', 'limit', 1], ['TT_HAN_PHA_HAM', 'Hạn Phá Quân hãm địa', 'limit', 1],
  ['TT_HAN_LOC_TON', 'Hạn Lộc Tồn:', 'support', 1], ['TT_HAN_KINH_TU_MO', 'Hạn Kình Dương ở Tứ mộ', 'support', 0.5],
  ['TT_HAN_HOA_TINH_DAC', 'Hạn Hỏa Tinh đắc địa', 'support', 1], ['TT_HAN_HOA_TINH_HAM', 'Hạn Hỏa Tinh hãm địa', 'limit', 1],
  ['TT_HAN_LINH_THAM', 'Hạn Linh Tinh gặp Tham Lang', 'support', 1], ['TT_HAN_MA', 'Hạn Thiên Mã gặp Tử, Phủ hoặc Lộc Tồn', 'support', 1],
  ['TT_HAN_HOA_LOC', 'Hạn Hóa Lộc:', 'support', 1], ['TT_HAN_HOA_QUYEN', 'Hạn Hóa Quyền:', 'support', 1],
  ['TT_HAN_HOA_KHOA', 'Hạn Hóa Khoa gặp Văn Xương', 'support', 1], ['TT_HAN_KY_SAT', 'Hạn Hóa Kỵ gặp sát tinh', 'limit', 1], ['TT_HAN_KY', 'Hạn Hóa Kỵ:', 'limit', 1],
].map(([id, prefix, side, w]) => ({ id: id as string, prefix: prefix as string, side: side as Side, w: w as number }))
  .sort((a, b) => b.prefix.length - a.prefix.length);
export const TT_WEIGHT = 0.6;
/** Khảo Luận pp.230-233: the tam hợp element of the vận against the birth year's (analysis.age_vs_dai_van). "cùng hành" reads "thoải mái,
 *  mức trung bình": no side, so it adds nothing. */
export const KL_RELATION: Record<string, { id: string; side: Side; w: number }> = {
  'đại vận sinh nhập cho tuổi': { id: 'KL_DV_SINH_NHAP', side: 'support', w: 1 },
  'tuổi khắc đại vận': { id: 'KL_DV_TUOI_KHAC_VAN', side: 'support', w: 0.6 },
  'tuổi sinh xuất cho đại vận': { id: 'KL_DV_SINH_XUAT', side: 'limit', w: 0.6 },
  'đại vận khắc tuổi': { id: 'KL_DV_VAN_KHAC_TUOI', side: 'limit', w: 1 },
};
export const LUU_THAI_TUE_WEIGHT = 0.5, LUU_HOA_WEIGHT = 0.3;
const LUU_HOA_ID: Record<string, string> = { 'Hóa Lộc': 'LUU_HOA_LOC', 'Hóa Quyền': 'LUU_HOA_QUYEN', 'Hóa Khoa': 'LUU_HOA_KHOA', 'Hóa Kỵ': 'LUU_HOA_KY' };
const LUU_HOA_CITE = 'thông lệ, chưa có trong ba sách (KL tr.41-42, TH tr.114 liệt kê chín sao lưu, không có Tứ Hóa)';

/** Corpus means of the raw ban_menh sums per palace name (engine/data/kg/index_norms.json, tools/interpret/index_norms.ts). */
export interface IndexNorms { version: string; kbVersion: string; charts: number; corpus: string; palace: Record<string, { support: number; limit: number }> }

interface Ctx {
  chart: ChartInput; k: Knowledge; norms: IndexNorms | null; byName: Map<string, Palace>; byBranch: Map<string, Palace>;
  natal: Map<string, Item[]>;                // verified natal items standing on each palace (scope 'self', weight before the scope factor)
  van: Map<string, Item[]>;                  // vận readings of each palace
}

/** Verified natal findings per palace, each weighed by its seat tier (with its own palace as centre) and rarity. */
function natalItems(chart: ChartInput, k: Knowledge): Map<string, Item[]> {
  const rmap = new Map<string, Rule>(k.rules.map(r => [r.id, r]));
  const guards = new Map((k.kg?.positionGuards ?? []).map(g => [g.ruleId, g]));
  const world: World = n => chart.base[`palace:${n}`] ? { ...(chart.base.chart ?? {}), ...chart.base[`palace:${n}`] } : null;
  const geo = new Map<string, Geo>();
  const out = new Map<string, Item[]>(chart.palaces.map(p => [p.name, []]));
  const seen = new Map<string, Item>();
  for (const f of run(k.rules, k.sources, chart.base).findings) {
    if (f.basis !== 'verified' || f.effect === 'neutral' || !f.palace || !out.has(f.palace)) continue;
    const rule = rmap.get(f.ruleId)!;
    const atoms = triggerAtoms(rule.conditions, { ...(chart.base.chart ?? {}), ...(chart.base[f.subject] ?? {}) }, world, f.palace);
    const gd = guards.get(f.ruleId);
    if (gd && !guardHolds(gd, atoms, chart.palaces, { here: f.palace, tuHoa: chart.tu_hoa })) continue;
    const g = geo.get(f.palace) ?? geo.set(f.palace, new Geo(chart, f.palace)).get(f.palace)!;
    const tiers = atoms.map(a => atomSeat(a, g)).filter(s => s && s.kind !== 'degree').map(s => s!.tier);
    const tier = (tiers.length ? Math.min(...tiers) : 5) as Tier;
    const w = r3(TIER_WEIGHT[tier] * (0.5 + rarity(k, f.ruleId)));
    // the same claim on the same palace (two books, two rules) counts once, at its strongest
    const key = `${f.palace}|${f.claim}|${f.effect}`, prev = seen.get(key);
    if (prev) { if (w > prev.w) Object.assign(prev, { id: f.ruleId, w, cite: rule.cites.join('; ') }); continue; }
    const item: Item = { id: f.ruleId, side: f.effect, w, layer: 'ban_menh', palace: f.palace, scope: 'self', cite: rule.cites.join('; '),
      text: (k.claims[f.claim] ?? rule.reading ?? f.claim).trim(), basis: 'sach' };
    seen.set(key, item);
    out.get(f.palace)!.push(item);
  }
  for (const xs of out.values()) xs.sort((a, b) => b.w - a.w || (a.id < b.id ? -1 : 1));
  return out;
}

/** The vận readings of every palace, from the facts' đại hạn list (one entry per palace). */
function vanItems(chart: ChartInput): Map<string, Item[]> {
  const out = new Map<string, Item[]>(chart.palaces.map(p => [p.name, []]));
  for (const d of chart.decades as Array<ChartInput['decades'][number] & { tt?: Array<{ text: string; src: string }>; kl?: { src: string; relation: string; verdict: string; xung_controlled: boolean } }>) {
    const list = out.get(d.palace);
    if (!list) continue;
    const add = (id: string, side: Side, w: number, cite: string, text: string, basis: ItemBasis) =>
      list.push({ id, side, w: r3(w), layer: 'van', palace: d.palace, scope: 'self', cite, text, basis });
    for (const r of d.readings as Array<{ text: string; src: string; rule_id?: string | null }>) {
      const t = r.rule_id ? VAN_RULES[r.rule_id] : undefined;
      if (t) add(r.rule_id!, t.side, t.w, r.src, r.text, 'sach');
    }
    for (const s of d.tt ?? []) {
      const t = TT_SENTENCES.find(x => s.text.startsWith(x.prefix));
      if (t) add(t.id, t.side, t.w * TT_WEIGHT, `${s.src} (diễn ý, chưa đối chiếu từng trang)`, s.text, 'sach_dien_giai');
    }
    if (d.kl) {
      const t = KL_RELATION[d.kl.relation];
      if (t) add(t.id, t.side, t.w, d.kl.src, `Tam hợp của cung vận so với tuổi: ${d.kl.relation}, sách đọc là ${d.kl.verdict}.`, 'sach');
      if (d.kl.xung_controlled) add('KL_DV_KHAC_XUNG', 'support', 0.5, d.kl.src, 'Tam hợp cung vận khắc tam hợp cung xung chiếu: theo sách nhận sao tốt, từ chối sao xấu của cung xung chiếu.', 'sach');
      // the Thái Tuế – Quan Phù – Bạch Hổ triad of KL p.233 is the same condition as VH_THAI_TUE / VH_QUAN_PHU / VH_BACH_HO above: not counted twice
    }
  }
  return out;
}

function context(chart: ChartInput, k: Knowledge, norms: IndexNorms | null): Ctx {
  return { chart, k, norms, byName: new Map(chart.palaces.map(p => [p.name, p])), byBranch: new Map(chart.palaces.map(p => [p.branch, p])),
    natal: natalItems(chart, k), van: vanItems(chart) };
}

/** The palace, its opposite and its two tam hợp, with the relation of each to the palace. */
function tamPhuong(c: Ctx, name: string): Array<{ p: Palace; rel: Rel }> {
  const t = c.byName.get(name)!;
  return c.chart.palaces.map(p => ({ p, rel: REL_OF[(p.branch_index - t.branch_index + 12) % 12] })).filter(x => x.rel)
    .sort((a, b) => ['self', 'opp', 'trine'].indexOf(a.rel) - ['self', 'opp', 'trine'].indexOf(b.rel) || a.p.branch_index - b.p.branch_index);
}

const sum = (xs: Item[], side: Side) => r3(xs.filter(x => x.side === side).reduce((a, x) => a + x.w, 0));

/** One layer of a score, for the "why" panel: what it adds on each side, and how (e.g. "tổng 12,4 so với trung bình 9,1"). */
export interface Part { layer: Layer; support: number; limit: number; note: string }
export interface Score { support: number; limit: number; parts: Part[]; items: Item[] }

/** Raw ban_menh sums of a palace: its own verified findings and those of its tam phương, scope-weighted (what the corpus norms average). */
export function natalRaw(c: Ctx, name: string): { support: number; limit: number; items: Item[] } {
  const items = tamPhuong(c, name).flatMap(({ p, rel }) => (c.natal.get(p.name) ?? []).map(x => ({ ...x, scope: rel, w: r3(x.w * SCOPE_WEIGHT[rel]) })));
  return { support: sum(items, 'support'), limit: sum(items, 'limit'), items };
}
/** Smoothing of the ratio: one plain finding (T1, rate 0.5: weight ≈ 0.63) rounded up. */
export const NORM_SMOOTH = 1;
/** ban_menh layer of a palace as a ratio to the corpus mean of the same palace: (sum + 1) / (mean + 1); 1 = the typical chart there. */
export function natalScore(c: Ctx, name: string): Score {
  const r = natalRaw(c, name), n = c.norms?.palace[name];
  const ratio = (x: number, m: number | undefined) => m === undefined ? r3(x) : r3((x + NORM_SMOOTH) / (m + NORM_SMOOTH));
  const support = ratio(r.support, n?.support), limit = ratio(r.limit, n?.limit);
  const note = n ? `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} so với trung bình ${vn(n.support)} / ${vn(n.limit)} của ${c.norms!.charts.toLocaleString('vi-VN')} lá số mẫu`
    : `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} (chưa có mức trung bình để so)`;
  return { support, limit, parts: [{ layer: 'ban_menh', support, limit, note }], items: r.items };
}

function combine(parts: Score[]): Score {
  return { support: r3(parts.reduce((a, p) => a + p.support, 0)), limit: r3(parts.reduce((a, p) => a + p.limit, 0)),
    parts: parts.flatMap(p => p.parts), items: parts.flatMap(p => p.items) };
}
const layerScore = (layer: Layer, items: Item[], note: string): Score => {
  const support = sum(items, 'support'), limit = sum(items, 'limit');
  return { support, limit, parts: items.length ? [{ layer, support, limit, note }] : [], items };
};
/** ban_menh + van of a palace read as a vận palace (đại hạn or tiểu hạn). */
function vanScore(c: Ctx, name: string): Score {
  const v = c.van.get(name) ?? [];
  return combine([natalScore(c, name), layerScore('van', v, `${v.length} câu sách về cung vận ${name}`)]);
}

/** Order of the radar: the twelve palaces from Mệnh round the board (tam phương 120° apart, the opposite palace across). */
function ring(c: Ctx): Palace[] {
  const m = c.byName.get('Mệnh')!;
  return [...c.chart.palaces].sort((a, b) => (a.branch_index - m.branch_index + 12) % 12 - (b.branch_index - m.branch_index + 12) % 12);
}

export interface DecadeIndex extends Score { index: number; palace: string; branch: string; age_from: number; age_to: number; year_from: number; year_to: number; current: boolean }
export interface YearIndex extends Score { year: number; age: number; can_chi: string; palace: string; branch: string; thai_tue: string; current: boolean }
export interface MonthIndex extends Score { month: number; palace: string }
export interface PalaceIndex extends Score { palace: string; branch: string }
export interface Indices {
  version: string; disclaimer: string; year: number;
  palaces: PalaceIndex[]; decades: DecadeIndex[]; years: YearIndex[];
  months: { year: number; basis: string; months: MonthIndex[] } | null;
  norms: { version: string; kbVersion: string; charts: number; corpus: string } | null;
  method: Record<string, string>;
}

/** Raw ban_menh sums of all twelve palaces of a chart (input of tools/interpret/index_norms.ts). */
export function natalRawAll(chart: ChartInput, k: Knowledge): Record<string, { support: number; limit: number }> {
  const c = context(chart, k, null);
  return Object.fromEntries(chart.palaces.map(p => { const r = natalRaw(c, p.name); return [p.name, { support: r.support, limit: r.limit }]; }));
}

/** All four indices for one chart; `year` is the facts' viewed year (facts.year.year). Deterministic: same facts, knowledge and norms → same output. */
export function computeIndices(chart: ChartInput, k: Knowledge, norms: IndexNorms | null, span = 10): Indices {
  const c = context(chart, k, norms);
  const Y0 = chart.year.year, born = chart.lunar_year;
  const palaces: PalaceIndex[] = ring(c).map(p => ({ palace: p.name, branch: p.branch, ...natalScore(c, p.name) }));
  const cur = chart.year.dai_han;
  const decades: DecadeIndex[] = chart.decades.slice(0, 10).map(d => ({
    index: d.index, palace: d.palace, branch: d.branch, age_from: d.age_from, age_to: d.age_to,
    year_from: born + d.age_from - 1, year_to: born + d.age_to - 1, current: !!cur && cur.age_from === d.age_from, ...vanScore(c, d.palace),
  }));

  // tiểu hạn of any year from the viewed year's (temporal.tuvi_year: one palace a year, forward for nam, backward for nữ)
  const dir = /nam$/i.test(chart.yin_yang_gender) ? 1 : -1;
  const b0 = BRANCHES.indexOf(chart.year.tieu_han_branch ?? '');
  // the Tứ Hóa of each stem, as the Python engine placed it for the đại hạn stems (one table, no copy of it here)
  const hoaOfStem = new Map<string, ChartInput['decades'][number]['hoa']>(chart.decades.map(d => [d.stem, d.hoa]));
  const years: YearIndex[] = [];
  if (b0 >= 0) for (let y = Y0 - span; y <= Y0 + span; y++) {
    const age = y - born + 1;
    if (age < 1) continue;
    const br = BRANCHES[(((b0 + (y - Y0) * dir) % 12) + 12) % 12];
    const p = c.byBranch.get(br)!;
    const stem = STEMS[(((y - 4) % 10) + 10) % 10], ybr = BRANCHES[(((y - 4) % 12) + 12) % 12];
    const tt = c.byBranch.get(ybr)!;
    const ttN = natalScore(c, tt.name);
    const luuTT = layerScore('luu_thai_tue', (['support', 'limit'] as Side[]).filter(s => ttN[s] > 0).map(s => ({
      id: `LUU_THAI_TUE@${tt.name}`, side: s, w: r3(ttN[s] * LUU_THAI_TUE_WEIGHT), layer: 'luu_thai_tue' as Layer, palace: tt.name, scope: 'self' as Rel,
      cite: 'vị trí: KL tr.41-42; nửa trọng số: quy ước hệ thống',
      text: `Lưu Thái Tuế năm ${stem} ${ybr} ở cung ${tt.name}: tính một nửa chỉ số bản mệnh của cung này (${s === 'support' ? 'thuận lợi' : 'thử thách'} ${vn(ttN[s])}).`,
      basis: 'thong_le' as ItemBasis })), `lưu Thái Tuế ở cung ${tt.name}, nửa trọng số`);
    const tp = new Map(tamPhuong(c, p.name).map(x => [x.p.name, x.rel]));
    const hoa = hoaOfStem.get(stem);
    const where = (r: Rel) => r === 'self' ? 'chính cung tiểu hạn' : r === 'opp' ? 'xung chiếu tiểu hạn' : 'tam hợp của tiểu hạn';
    const luuHoa = layerScore('luu_tu_hoa', hoa ? Object.entries(hoa).filter(([, v]) => v.palace && tp.has(v.palace)).map(([h, v]) => ({
      id: LUU_HOA_ID[h] ?? `LUU_${h}`, side: (h === 'Hóa Kỵ' ? 'limit' : 'support') as Side, w: r3(LUU_HOA_WEIGHT * SCOPE_WEIGHT[tp.get(v.palace!)!]),
      layer: 'luu_tu_hoa' as Layer, palace: v.palace!, scope: tp.get(v.palace!)!, cite: LUU_HOA_CITE,
      text: `Lưu ${h} năm ${stem} (trên ${v.star}) ở cung ${v.palace}, ${where(tp.get(v.palace!)!)}.`, basis: 'thong_le' as ItemBasis })) : [],
      'lưu Tứ Hóa theo can năm (thông lệ), trọng số thấp');
    years.push({ year: y, age, can_chi: `${stem} ${ybr}`, palace: p.name, branch: br, thai_tue: tt.name, current: y === Y0, ...combine([vanScore(c, p.name), luuTT, luuHoa]) });
  }

  const ng = chart.year as ChartInput['year'] & { nguyet_han?: Record<string, number> | null };
  const months = ng.nguyet_han ? { year: Y0, basis: 'TH tr.115 (vị trí tháng); mức của tháng = chỉ số bản mệnh của cung nguyệt hạn',
    months: Object.entries(ng.nguyet_han).map(([palace, month]) => ({ month, palace, ...natalScore(c, palace) })).sort((a, b) => a.month - b.month) } : null;

  return {
    version: INDICES_VERSION, disclaimer: DISCLAIMER, year: Y0, palaces, decades, years, months,
    norms: norms && { version: norms.version, kbVersion: norms.kbVersion, charts: norms.charts, corpus: norms.corpus },
    method: {
      ban_menh: 'nhận định đã đối chiếu sách bắn vào cung, cung xung chiếu và hai cung tam hợp; trọng số = tầng của nhận định × (0,5 + độ hiếm) × vị trí (chính cung 1, xung chiếu 0,85, tam hợp 0,7); so với mức trung bình của chính cung đó trên bộ lá số mẫu: (tổng + 1) / (trung bình + 1), 1 là mức thường gặp (quy ước hệ thống)',
      van: 'câu sách về cung vận: Khảo Luận tr.230-236, Thực Hành tr.115-117 (trọng số 1 hoặc 0,5), Toàn Thư tr.97-105 (diễn ý, × 0,6)',
      luu_thai_tue: 'năm: một nửa chỉ số bản mệnh của cung lưu Thái Tuế (vị trí KL tr.41-42, trọng số là quy ước)',
      luu_tu_hoa: 'năm: Tứ Hóa theo can năm rơi vào tam phương tiểu hạn, trọng số 0,3 × vị trí (thông lệ, không có trong ba sách)',
      nguyet: 'tháng: chỉ vị trí cung nguyệt hạn có nguồn (TH tr.115); mức là chỉ số bản mệnh của cung đó',
    },
  };
}
