// System indices for the "Tổng quan lá số" charts (docs/PRODUCT-PLAN.md phase 1.1–1.4). Two different things are measured, and kept apart:
//
//   1. the NATAL quality of each palace (the radar): verified natal findings of the rule engine (engine.ts) on the palace and its tam phương,
//      told as a ratio to the mean of the same palace over the 1,000-chart corpus. This never moves with time.
//   2. how a PERIOD (đại vận, year, month) activates the whole chart. Each period is a sum of layers; every layer is a raw net value
//      (support − limit of its items) turned into a z-score against corpus1000 (engine/data/kg/index_norms.json, tools/interpret/index_norms.ts),
//      so all layers share one unit before they are weighted and added. The sum is then placed on a five-level scale by the corpus quantiles
//      (12 / 33 / 67 / 88 %). Natal findings are never listed as the reason of a period: the period palace's natal quality is a background
//      layer only (≤ 30 % of the weights). Book layers decide the direction; convention layers only modulate it (conventionCap).
//
// Đại vận layers
//   hoa_van  the Tứ Hóa of the decade stem (facts.decades[].hoa) landing on the decade palace, its tam phương or Mệnh. Common convention
//            (phi hóa theo can đại vận); the three books give no sentence for it, so its items are labelled thong_le.
//   van      the book sentences about the vận palace: Khảo Luận pp.233-236 and Thực Hành pp.115-117 (van_han_rules.json, by rule id), Khảo
//            Luận pp.230-233 (tam hợp of the vận against the birth year), Toàn Thư pp.97-105 nhập hạn ca (paraphrased, page check pending: ×0.5).
//   nen      background: the natal quality of the decade palace (radar ratio support − limit).
//   vung     the robustness of the whole chart (Mệnh and its tam phương on the radar scale: verified findings only, book cách cục
//            included; the draft formations of reason/structures.ts stay out): a strong chart lifts a good decade and softens a bad one.
//            The modifier is a system convention: value = base × VUNG_GAIN × clamp(z) × sign(base).
// Year layers
//   dai_van       the score of the đại vận the year falls in (≈ 40 %).
//   tieu_han      the book sentences about the tiểu hạn palace (same sources as van; facts.year.tieu_han_tt / tieu_han_kl for the viewed year).
//   nen           background: natal quality of the tiểu hạn palace.
//   luu_thai_tue  natal quality of the palace the year's Thái Tuế stands in (position KL tr.41-42; using its quality is a convention).
//   luu_sao       Thực Hành tr.114: lưu Khốc, Hư meeting the tiểu hạn are bad, with hung tinh "năm đầy tai ương" (positions KL tr.41-42).
//   luu_sao_tl    the other lưu stars in reach (Kình, Đà as sát tinh, Lộc Tồn; Khốc, Hư off the tiểu hạn): side of their kind, convention.
//                 KL tr.41: the lưu stars are "nhất thời, không nặng ký" — hence the low weights.
//   luu_tu_hoa    the Tứ Hóa of the year stem on the tiểu hạn's tam phương or Mệnh: convention, not in the three books (low weight, labelled).
// Month: the viewed year's score plus a small term for the natal quality of the nguyệt hạn palace (position TH tr.115); only a position.
//
// Bát Tự strip: the luck pillars of the Bát Tự chart on the same time axis, tagged by whether they carry the điều hậu stems of Thiệu Vĩ Hoa's
// table (TVH pp.389-396, via facts.bazi.deep). It is shown beside the decades, never added to the Tử Vi score.
import type { ChartInput, Knowledge, Palace, Rule } from './types.ts';
import { run } from './engine.ts';
import { triggerAtoms } from './kg/atoms.ts';
import type { World } from './dsl.ts';
import { Geo, SCOPE_WEIGHT, TIER_WEIGHT, atomSeat, rarity, type Tier } from './reason/tiers.ts';
import { guardHolds } from './reason/positions.ts';
import { SAT } from './reason/structures.ts';

export const INDICES_VERSION = 'indices-2.1.0';
export const DISCLAIMER = 'Mức tổng hợp từ câu sách và thông lệ có ghi nhãn, so với 1.000 lá số mẫu; không phải xác suất hay dự báo.';

export type Side = 'support' | 'limit';
export type Layer = 'ban_menh' | 'hoa_van' | 'van' | 'nen' | 'vung' | 'dai_van' | 'tieu_han' | 'luu_thai_tue' | 'luu_sao' | 'luu_sao_tl' | 'luu_tu_hoa' | 'thong_le_cap' | 'nam' | 'nguyet';
/** sach: a book sentence with its page; sach_dien_giai: a paraphrased book passage whose page is still to be checked; thong_le: convention;
 *  nhap: an experimental definition (draft cách cục) */
export type ItemBasis = 'sach' | 'sach_dien_giai' | 'thong_le' | 'nhap';
export type Rel = 'self' | 'opp' | 'trine' | 'menh';
export interface Item {
  id: string; side: Side; w: number; layer: Layer; palace: string; scope: Rel; cite: string; text: string; basis: ItemBasis;
  /** the reading as a clause for the period sentences ("vận có Tham Lang ở Dậu thì hao tài, phóng túng") and its book */
  gist?: string; book?: string;
}

const r3 = (x: number) => Math.round(x * 1000) / 1000;
/** A number as Vietnamese text: decimal comma, two places. */
const vn = (x: number) => String(Math.round(x * 100) / 100).replace('.', ',');
const STEMS = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const REL_OF: Record<number, Exclude<Rel, 'menh'>> = { 0: 'self', 6: 'opp', 4: 'trine', 8: 'trine' };
/** Distance weights of a period item: the reasoner's scope weights; Mệnh (when outside the tam phương) 0.6 — system convention. */
export const REL_W: Record<Rel, number> = { self: SCOPE_WEIGHT.self, opp: SCOPE_WEIGHT.opp, trine: SCOPE_WEIGHT.trine, menh: 0.6 };
/** What each palace is about (engine/tvbt/van_han.py DOMAIN, the topic the tiểu hạn reading already names). */
export const DOMAIN: Record<string, string> = { 'Mệnh': 'chính mình', 'Phụ Mẫu': 'cha mẹ, người bề trên', 'Phúc Đức': 'đời sống tinh thần, họ hàng',
  'Điền Trạch': 'nhà cửa, đất đai', 'Quan Lộc': 'công danh, sự nghiệp', 'Nô Bộc': 'bạn bè, người cộng tác', 'Thiên Di': 'giao thiệp bên ngoài, đi xa',
  'Tật Ách': 'thể trạng', 'Tài Bạch': 'tiền bạc', 'Tử Tức': 'con cái', 'Phu Thê': 'hôn nhân', 'Huynh Đệ': 'anh chị em' };

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
/** Toàn Thư nhập hạn ca is a paraphrase whose pages are still to be checked: low weight. */
export const TT_WEIGHT = 0.5;
/** Khảo Luận pp.230-233: the tam hợp element of the vận against the birth year's (analysis.age_vs_dai_van). "cùng hành" reads "thoải mái,
 *  mức trung bình": no side, so it adds nothing. */
export const KL_RELATION: Record<string, { id: string; side: Side; w: number }> = {
  'đại vận sinh nhập cho tuổi': { id: 'KL_DV_SINH_NHAP', side: 'support', w: 1 },
  'tuổi khắc đại vận': { id: 'KL_DV_TUOI_KHAC_VAN', side: 'support', w: 0.6 },
  'tuổi sinh xuất cho đại vận': { id: 'KL_DV_SINH_XUAT', side: 'limit', w: 0.6 },
  'đại vận khắc tuổi': { id: 'KL_DV_VAN_KHAC_TUOI', side: 'limit', w: 1 },
};
const HOA_ID: Record<string, string> = { 'Hóa Lộc': 'LOC', 'Hóa Quyền': 'QUYEN', 'Hóa Khoa': 'KHOA', 'Hóa Kỵ': 'KY' };
const DV_HOA_CITE = 'thông lệ (Tứ Hóa theo can đại vận, phép phi hóa); ba sách không có câu luận cho lớp này';
const LUU_HOA_CITE = 'thông lệ, chưa có trong ba sách (KL tr.41-42, TH tr.114 liệt kê chín sao lưu, không có Tứ Hóa)';
const LUU_POS_CITE = 'vị trí: KL tr.41-42 (cùng chín sao ở TH tr.114)';

// ---- weights of the period layers (system convention; each layer is a z-score first, so the weights compare like with like) ----
// Book evidence decides the direction (owner rule 2026-10-21: a convention never overrules a book sentence): the sourced layers carry most of
// the weight, and the convention layers (CONVENTION) only modulate — their sum is capped at CONV_K × |sourced part| (+ CONV_FLOOR when they
// point the same way or the books are silent), so they can strengthen or soften the books' direction but never flip it.
export const W_DECADE = { van: 0.65, nen: 0.1, hoa_van: 0.25 } as const;
export const VUNG_GAIN = 0.15, VUNG_CLAMP = 1.5;
export const W_YEAR = { dai_van: 0.4, tieu_han: 0.27, nen: 0.08, luu_sao: 0.1, luu_thai_tue: 0.04, luu_sao_tl: 0.04, luu_tu_hoa: 0.07 } as const;
export const CONVENTION: ReadonlySet<Layer> = new Set<Layer>(['hoa_van', 'luu_tu_hoa', 'luu_thai_tue', 'luu_sao_tl']);
export const CONV_K = 0.5, CONV_FLOOR = 0.15;
export const W_MONTH = 0.25;
/** The five levels, from the corpus quantiles 10 / 30 / 70 / 90 % of each kind of period. */
export const LEVELS = ['Rất thử thách', 'Nhiều thử thách', 'Trung bình', 'Thuận', 'Rất thuận'] as const;
export const LEVEL_Q = [0.12, 0.33, 0.67, 0.88];
const FALLBACK_CUTS = [-1.175, -0.44, 0.44, 1.175];   // the same quantiles of a unit normal, when no corpus norms are loaded

/** Corpus norms (engine/data/kg/index_norms.json, tools/interpret/index_norms.ts). */
export interface LayerNorm { mean: number; sd: number }
export interface IndexNorms {
  version: string; kbVersion: string; charts: number; corpus: string;
  /** mean raw natal sums per palace name (the radar) */
  palace: Record<string, { support: number; limit: number }>;
  /** mean and spread of every period layer's raw net value */
  layers?: Record<string, LayerNorm>;
  /** level cut points per kind of period (LEVEL_Q quantiles of the scores) */
  cuts?: { decade: number[]; year: number[]; month: number[] };
}

// ================================================================ natal (radar) ================================================================

/** Verified natal findings per palace, each weighed by its seat tier (with its own palace as centre) and rarity on that palace. */
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
    // rarity on the palace the finding stands on (kg.baseRates.palaces), not on Mệnh
    const w = r3(TIER_WEIGHT[tier] * (0.5 + rarity(k, f.ruleId, f.palace)));
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

type Ctx = { chart: ChartInput; byName: Map<string, Palace>; byBranch: Map<string, Palace>; byIndex: Map<number, Palace>; natal: Map<string, Item[]> };
function context(chart: ChartInput, k: Knowledge): Ctx {
  return { chart, byName: new Map(chart.palaces.map(p => [p.name, p])), byBranch: new Map(chart.palaces.map(p => [p.branch, p])),
    byIndex: new Map(chart.palaces.map(p => [p.branch_index, p])), natal: natalItems(chart, k) };
}

/** The palace, its opposite and its two tam hợp, with the relation of each to the palace. */
function tamPhuong(c: Ctx, name: string): Array<{ p: Palace; rel: Exclude<Rel, 'menh'> }> {
  const t = c.byName.get(name)!;
  return c.chart.palaces.map(p => ({ p, rel: REL_OF[(p.branch_index - t.branch_index + 12) % 12] })).filter(x => x.rel)
    .sort((a, b) => ['self', 'opp', 'trine'].indexOf(a.rel) - ['self', 'opp', 'trine'].indexOf(b.rel) || a.p.branch_index - b.p.branch_index);
}
/** Where a palace stands from a period palace: in its tam phương, else Mệnh, else out of reach. */
function reach(c: Ctx, from: string, to: string | null | undefined): Rel | null {
  if (!to) return null;
  const r = tamPhuong(c, from).find(x => x.p.name === to)?.rel;
  return r ?? (to === 'Mệnh' ? 'menh' : null);
}

const sum = (xs: Item[], side: Side) => r3(xs.filter(x => x.side === side).reduce((a, x) => a + x.w, 0));
const net = (xs: Item[]) => r3(sum(xs, 'support') - sum(xs, 'limit'));

/** Raw natal sums of a palace: its own verified findings and those of its tam phương, scope-weighted (what the corpus norms average). */
function natalRaw(c: Ctx, name: string): { support: number; limit: number; items: Item[] } {
  const items = tamPhuong(c, name).flatMap(({ p, rel }) => (c.natal.get(p.name) ?? []).map(x => ({ ...x, scope: rel, w: r3(x.w * SCOPE_WEIGHT[rel]) })));
  return { support: sum(items, 'support'), limit: sum(items, 'limit'), items };
}
/** Smoothing of the radar ratio: one plain finding rounded up. */
export const NORM_SMOOTH = 1;
export interface PalaceIndex { palace: string; branch: string; support: number; limit: number; note: string; items: Item[] }
/** Natal quality of a palace as a ratio to the corpus mean of the same palace: (sum + 1) / (mean + 1); 1 = the typical chart there. */
function natalIndex(c: Ctx, name: string, norms: IndexNorms | null): PalaceIndex {
  const r = natalRaw(c, name), n = norms?.palace[name];
  const ratio = (x: number, m: number | undefined) => m === undefined ? r3(x) : r3((x + NORM_SMOOTH) / (m + NORM_SMOOTH));
  const note = n ? `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} so với trung bình ${vn(n.support)} / ${vn(n.limit)} của ${norms!.charts.toLocaleString('vi-VN')} lá số mẫu`
    : `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} (chưa có mức trung bình để so)`;
  return { palace: name, branch: c.byName.get(name)!.branch, support: ratio(r.support, n?.support), limit: ratio(r.limit, n?.limit), note, items: r.items };
}

/** Raw natal sums of all twelve palaces of a chart (input of tools/interpret/index_norms.ts). */
export function natalRawAll(chart: ChartInput, k: Knowledge): Record<string, { support: number; limit: number }> {
  const c = context(chart, k);
  return Object.fromEntries(chart.palaces.map(p => { const r = natalRaw(c, p.name); return [p.name, { support: r.support, limit: r.limit }]; }));
}

// ================================================================ period items ================================================================

const bookOf = (cite: string) => /Khảo Luận|KL /.test(cite) ? 'Khảo Luận' : /Thực Hành|TH /.test(cite) ? 'Thực Hành' : /Toàn Thư|TT /.test(cite) ? 'Toàn Thư' : undefined;
const LOWER_LEAD = /^(Cung|Vận|Hạn|Tam|Lưu)\b/;
const lowerLead = (s: string) => LOWER_LEAD.test(s) ? s[0].toLowerCase() + s.slice(1) : s;
/** "Vận có Tham Lang ở Dậu: theo sách hao tài, phóng túng." → "vận có Tham Lang ở Dậu thì hao tài, phóng túng". */
export function gistOf(text: string): string {
  const t = text.trim().replace(/\.\s*$/, '').split('; ')[0];
  const i = t.indexOf(': ');
  if (i < 0) return lowerLead(t);
  const cond = t.slice(0, i), rest = t.slice(i + 2).replace(/^(theo sách|sách xem|sách đọc là|sách cho là)\s+/, '');
  const glue = /^(là|đây|đó|cung vận này|cung vận có)\b/.test(rest) ? ', ' : ' thì ';
  return `${lowerLead(cond)}${glue}${rest.replace(/^là /, 'đó là ')}`;
}

type DecadeFacts = ChartInput['decades'][number] & { tt?: Array<{ text: string; src: string }>;
  kl?: { src: string; relation: string; verdict: string; xung_controlled: boolean; event?: string | null } | null };

/** The book sentences of a vận palace (đại hạn or tiểu hạn): rule-id readings, Toàn Thư paraphrases, Khảo Luận pp.230-233 facts. */
function vanItems(palace: string, layer: Layer, readings: DecadeFacts['readings'], tt: DecadeFacts['tt'], kl: DecadeFacts['kl']): Item[] {
  const list: Item[] = [];
  const add = (it: Omit<Item, 'layer' | 'palace' | 'scope' | 'book'>) => list.push({ ...it, w: r3(it.w), layer, palace, scope: 'self', book: bookOf(it.cite) });
  for (const r of readings as Array<{ text: string; src: string; rule_id?: string | null }>) {
    const t = r.rule_id ? VAN_RULES[r.rule_id] : undefined;
    if (t) add({ id: r.rule_id!, side: t.side, w: t.w, cite: r.src, text: r.text, basis: 'sach', gist: gistOf(r.text) });
  }
  for (const s of tt ?? []) {
    const t = TT_SENTENCES.find(x => s.text.startsWith(x.prefix));
    if (t) add({ id: t.id, side: t.side, w: t.w * TT_WEIGHT, cite: `${s.src} (diễn ý, chưa đối chiếu từng trang)`, text: s.text, basis: 'sach_dien_giai', gist: gistOf(s.text) });
  }
  if (kl) {
    const t = KL_RELATION[kl.relation];
    if (t) add({ id: t.id, side: t.side, w: t.w, cite: kl.src, basis: 'sach',
      text: `Tam hợp của cung vận so với tuổi: ${kl.relation}, sách đọc là ${kl.verdict}.`,
      gist: `hành tam hợp của cung vận và của tuổi ở thế “${kl.relation}”, sách đọc là ${kl.verdict}` });
    if (kl.xung_controlled) add({ id: 'KL_DV_KHAC_XUNG', side: 'support', w: 0.5, cite: kl.src, basis: 'sach',
      text: 'Tam hợp cung vận khắc tam hợp cung xung chiếu: theo sách nhận sao tốt, từ chối sao xấu của cung xung chiếu.',
      gist: 'tam hợp cung vận khắc tam hợp cung xung chiếu, nên nhận sao tốt và từ chối sao xấu của cung ấy' });
    // the Thái Tuế – Quan Phù – Bạch Hổ triad of KL p.233 is the same condition as VH_THAI_TUE / VH_QUAN_PHU / VH_BACH_HO above: not counted twice
  }
  return list;
}

/** Tứ Hóa of a stem landing within reach of a period palace (its tam phương or Mệnh). */
function hoaItems(c: Ctx, hoa: ChartInput['decades'][number]['hoa'] | undefined, at: string, layer: 'hoa_van' | 'luu_tu_hoa', stem: string, scale = 1): Item[] {
  const out: Item[] = [];
  for (const [h, v] of Object.entries(hoa ?? {})) {
    const rel = reach(c, at, v.palace);
    if (!rel) continue;
    const id = `${layer === 'hoa_van' ? 'DV' : 'LUU'}_HOA_${HOA_ID[h] ?? h}`;
    out.push({ id, side: h === 'Hóa Kỵ' ? 'limit' : 'support', w: r3(REL_W[rel] * scale), layer, palace: v.palace!, scope: rel, basis: 'thong_le',
      cite: layer === 'hoa_van' ? DV_HOA_CITE : LUU_HOA_CITE,
      text: `${h} của can ${stem} (trên ${v.star}) vào cung ${v.palace}${rel === 'menh' ? '' : `, ${REL_VI[rel]} của cung ${layer === 'hoa_van' ? 'đại vận' : 'tiểu hạn'}`}.` });
  }
  return out;
}
const REL_VI: Record<Rel, string> = { self: 'chính cung', opp: 'xung chiếu', trine: 'tam hợp', menh: 'Mệnh' };

// ---- the nine lưu stars (KL tr.41-42; TH tr.114) for any year: positions from the year stem and branch, as engine/tvbt/reasoning/temporal_facts.luu_tinh ----
const LOC_TON = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0];          // KL tr.42 bảng Lưu Lộc Tồn: Giáp Dần, Ất Mão, Bính/Mậu Tỵ, Đinh/Kỷ Ngọ, Canh Thân, Tân Dậu, Nhâm Hợi, Quý Tý
const MA = [2, 11, 8, 5];                                  // KL tr.42: Thân Tý Thìn → Dần, Tỵ Dậu Sửu → Hợi, Dần Ngọ Tuất → Thân, Hợi Mão Mùi → Tỵ
export function luuStars(chart: ChartInput, year: number): Record<string, string> {
  const ys = (((year - 4) % 10) + 10) % 10, yb = (((year - 4) % 12) + 12) % 12, lt = LOC_TON[ys];
  const fwd = chart.yin_yang_gender === 'dương nam' || chart.yin_yang_gender === 'âm nữ';
  const pos: Record<string, number> = { 'Thái Tuế': yb, 'Tang Môn': yb + 2, 'Bạch Hổ': yb + 8, 'Thiên Khốc': 6 - yb, 'Thiên Hư': 6 + yb,
    'Lộc Tồn': lt, 'Kình Dương': lt + (fwd ? 1 : -1), 'Đà La': lt - (fwd ? 1 : -1), 'Thiên Mã': MA[yb % 4] };
  const byIndex = new Map(chart.palaces.map(p => [p.branch_index, p.name]));
  return Object.fromEntries(Object.entries(pos).map(([k, v]) => [k, byIndex.get(((v % 12) + 12) % 12)!]));
}
/** The side a lưu star takes. Khốc, Hư: TH tr.114 ("gặp hai Khốc, Hư là xấu") at the tiểu hạn itself; elsewhere in reach and for Kình, Đà
 *  (sát tinh) and Lộc Tồn the side of their kind is a convention. Thái Tuế, Tang Môn, Bạch Hổ, Thiên Mã: positions only, no side. */
const LUU_SIDE: Record<string, Side> = { 'Thiên Khốc': 'limit', 'Thiên Hư': 'limit', 'Kình Dương': 'limit', 'Đà La': 'limit', 'Lộc Tồn': 'support' };
const LUU_ID: Record<string, string> = { 'Thiên Khốc': 'LUU_KHOC', 'Thiên Hư': 'LUU_HU', 'Kình Dương': 'LUU_KINH', 'Đà La': 'LUU_DA', 'Lộc Tồn': 'LUU_LOC_TON' };
function luuItems(c: Ctx, th: string, luu: Record<string, string>): Item[] {
  const out: Item[] = [];
  for (const [star, side] of Object.entries(LUU_SIDE)) {
    const at = luu[star], rel = reach(c, th, at);
    if (!rel) continue;
    const book = (star === 'Thiên Khốc' || star === 'Thiên Hư') && rel === 'self';
    out.push({ id: LUU_ID[star], side, w: REL_W[rel], layer: 'luu_sao', palace: at, scope: rel, basis: book ? 'sach' : 'thong_le', book: book ? 'Thực Hành' : undefined,
      cite: book ? `${LUU_POS_CITE}; nghĩa: TH tr.114 (“gặp hai Khốc, Hư là xấu”)` : `${LUU_POS_CITE}; bên ${side === 'limit' ? 'bất lợi' : 'thuận'} theo loại sao: thông lệ`,
      text: `Lưu ${star} ở cung ${at}${rel === 'self' ? ', ngay cung tiểu hạn' : rel === 'menh' ? '' : `, ${REL_VI[rel]} của tiểu hạn`}.` });
  }
  // TH tr.114: Khốc, Hư at the tiểu hạn "nếu có thêm các hung tinh thì ấy là năm đầy tai ương, nước mắt"
  const kh = ['Thiên Khốc', 'Thiên Hư'].filter(s => luu[s] === th);
  const hung = [...['Kình Dương', 'Đà La'].filter(s => luu[s] === th).map(s => `lưu ${s}`), ...SAT.filter(s => c.byName.get(th)!.stars.includes(s))];
  if (kh.length && hung.length) out.push({ id: 'TH_LUU_KHOC_HU_HUNG', side: 'limit', w: 1, layer: 'luu_sao', palace: th, scope: 'self', basis: 'sach', book: 'Thực Hành',
    cite: 'TH tr.114', text: `Lưu ${kh.join(', ')} gặp hung tinh (${hung.join(', ')}) ngay cung tiểu hạn: Thực Hành gọi là năm đầy tai ương, nước mắt.` });
  return out;
}

// ================================================================ period inputs (raw) ================================================================

/** One raw layer of a period: its net value before the corpus z-score, and the items behind it. */
export interface RawLayer { layer: Layer; raw: number; items: Item[]; note: string; basis: ItemBasis | 'tinh_toan' }
export interface DecadeRaw { d: DecadeFacts; layers: RawLayer[] }
export interface YearRaw { year: number; age: number; can_chi: string; palace: string; branch: string; thai_tue: string; decade: number | null; layers: RawLayer[]; luu: Record<string, string> }
export interface PeriodInputs {
  Y0: number;
  palaces: PalaceIndex[];                     // radar (needs norms.palace; computed with the norms given)
  natalNet: Record<string, number>;           // radar support − limit per palace
  vung: RawLayer;
  decades: DecadeRaw[]; years: YearRaw[]; months: Array<{ month: number; palace: string; layer: RawLayer }> | null;
}

/** Robustness of the whole chart: the natal quality of Mệnh and its tam phương on the radar scale (verified book findings only, the book
 *  cách cục among them). The experimental cách cục of reason/structures.ts are all draft, so they stay out of this live score. */
function vungLayer(natalNet: Record<string, number>): RawLayer {
  const m = natalNet['Mệnh'] ?? 0;
  return { layer: 'vung', raw: m, items: [], basis: 'sach', note: `Mệnh và tam phương (thuận − thử thách so với mức thường gặp) ${vn(m)}` };
}

export function periodInputs(chart: ChartInput, k: Knowledge, norms: IndexNorms | null, span = 10): PeriodInputs {
  const c = context(chart, k);
  const m = c.byName.get('Mệnh')!;
  const palaces = [...chart.palaces].sort((a, b) => (a.branch_index - m.branch_index + 12) % 12 - (b.branch_index - m.branch_index + 12) % 12)
    .map(p => natalIndex(c, p.name, norms));
  const natalNet = Object.fromEntries(palaces.map(p => [p.palace, r3(p.support - p.limit)]));
  const nen = (palace: string, layer: Layer, what: string): RawLayer => ({ layer, raw: natalNet[palace] ?? 0, items: [], basis: 'tinh_toan',
    note: `${what} cung ${palace}: chất lượng bẩm sinh (thuận − thử thách so với mức thường gặp) ${vn(natalNet[palace] ?? 0)}` });

  const vanOf = new Map<string, DecadeFacts>((chart.decades as DecadeFacts[]).map(d => [d.palace, d]));
  const decades: DecadeRaw[] = (chart.decades as DecadeFacts[]).slice(0, 10).map(d => {
    const hv = hoaItems(c, d.hoa, d.palace, 'hoa_van', d.stem), vv = vanItems(d.palace, 'van', d.readings, d.tt, d.kl);
    return { d, layers: [
      { layer: 'hoa_van', raw: net(hv), items: hv, basis: 'thong_le', note: `Tứ Hóa theo can ${d.stem}: ${hv.length} hóa trong tam phương cung vận hoặc Mệnh` },
      { layer: 'van', raw: net(vv), items: vv, basis: 'sach', note: `${vv.length} câu sách về cung vận ${d.palace}` },
      nen(d.palace, 'nen', 'nền:'),
    ] };
  });

  // tiểu hạn of any year from the viewed year's (temporal.tuvi_year: one palace a year, forward for nam, backward for nữ)
  const Y0 = chart.year.year, born = chart.lunar_year;
  const dir = /nam$/i.test(chart.yin_yang_gender) ? 1 : -1;
  const b0 = BRANCHES.indexOf(chart.year.tieu_han_branch ?? '');
  // the Tứ Hóa of each stem, as the Python engine placed it for the đại hạn stems (one table, no copy of it here)
  const hoaOfStem = new Map<string, ChartInput['decades'][number]['hoa']>(chart.decades.map(d => [d.stem, d.hoa]));
  const yf = chart.year as ChartInput['year'] & { tieu_han_tt?: DecadeFacts['tt']; tieu_han_kl?: DecadeFacts['kl'] };
  const years: YearRaw[] = [];
  if (b0 >= 0) for (let y = Y0 - span; y <= Y0 + span; y++) {
    const age = y - born + 1;
    if (age < 1) continue;
    const br = BRANCHES[(((b0 + (y - Y0) * dir) % 12) + 12) % 12];
    const p = c.byBranch.get(br)!;
    const stem = STEMS[(((y - 4) % 10) + 10) % 10], ybr = BRANCHES[(((y - 4) % 12) + 12) % 12];
    const tt = c.byBranch.get(ybr)!;
    const di = chart.decades.slice(0, 10).findIndex(d => d.age_from <= age && age <= d.age_to);
    const vd = vanOf.get(p.name);
    // the viewed year carries its own Toàn Thư / Khảo Luận facts for the tiểu hạn palace (facts.year); they equal the decade entry of that palace
    const th = vanItems(p.name, 'tieu_han', vd?.readings ?? [], y === Y0 && yf.tieu_han_tt ? yf.tieu_han_tt : vd?.tt, y === Y0 && yf.tieu_han_kl ? yf.tieu_han_kl : vd?.kl);
    const luu = luuStars(chart, y);
    const all = luuItems(c, p.name, luu), lh = hoaItems(c, hoaOfStem.get(stem), p.name, 'luu_tu_hoa', stem);
    // the lưu stars split by basis: TH tr.114 (Khốc, Hư at the tiểu hạn) is book; the side of Kình, Đà, Lộc Tồn and of Khốc, Hư elsewhere is convention
    const ls = all.filter(i => i.basis === 'sach'), lt = all.filter(i => i.basis !== 'sach').map(i => ({ ...i, layer: 'luu_sao_tl' as Layer }));
    years.push({ year: y, age, can_chi: `${stem} ${ybr}`, palace: p.name, branch: br, thai_tue: tt.name, decade: di >= 0 ? di : null, luu, layers: [
      { layer: 'tieu_han', raw: net(th), items: th, basis: 'sach', note: `${th.length} câu sách về cung tiểu hạn ${p.name}` },
      nen(p.name, 'nen', 'nền: tiểu hạn ở'),
      { ...nen(tt.name, 'luu_thai_tue', 'lưu Thái Tuế ở'), basis: 'thong_le' },
      { layer: 'luu_sao', raw: net(ls), items: ls, basis: 'sach', note: `Thực Hành tr.114: lưu Khốc, Hư ở cung tiểu hạn năm ${stem} ${ybr}: ${ls.length}` },
      { layer: 'luu_sao_tl', raw: net(lt), items: lt, basis: 'thong_le', note: `sao lưu năm ${stem} ${ybr} theo loại sao, trong tầm tiểu hạn hoặc Mệnh: ${lt.length}` },
      { layer: 'luu_tu_hoa', raw: net(lh), items: lh, basis: 'thong_le', note: `lưu Tứ Hóa theo can ${stem} trong tầm tiểu hạn hoặc Mệnh: ${lh.length}` },
    ] });
  }
  const ng = (chart.year as ChartInput['year'] & { nguyet_han?: Record<string, number> | null }).nguyet_han;
  const months = ng ? Object.entries(ng).map(([palace, month]) => ({ month, palace, layer: nen(palace, 'nguyet', 'nguyệt hạn ở') })).sort((a, b) => a.month - b.month) : null;
  return { Y0, palaces, natalNet, vung: vungLayer(natalNet), decades, years, months };
}

// ================================================================ scoring ================================================================

/** One layer of a period score: raw net, its z-score against the corpus, its weight and what it adds (value = weight × z). */
export interface Part { layer: Layer; raw: number; z: number; weight: number; value: number; note: string; basis: ItemBasis | 'tinh_toan' }
export interface Period { score: number; level: number; level_vi: string; parts: Part[]; items: Item[]; text: string[] }
export interface DecadeIndex extends Period { index: number; palace: string; branch: string; stem: string; age_from: number; age_to: number; year_from: number; year_to: number; current: boolean }
export interface YearIndex extends Period { year: number; age: number; can_chi: string; palace: string; branch: string; thai_tue: string; current: boolean; decade: number | null }
export interface MonthIndex extends Period { month: number; palace: string }
export interface BaziStrip {
  basis: string; cell: string | null; note: string;
  pillars: Array<{ index: number; pillar: string; age_from: number; year_from: number | null; year_to: number | null; tag: 'dung' | 'hy' | 'khong';
    tag_vi: string; reduced: string | null; current: boolean }>;
}
export interface Indices {
  version: string; disclaimer: string; year: number; levels: readonly string[];
  palaces: PalaceIndex[]; decades: DecadeIndex[]; years: YearIndex[];
  months: { year: number; basis: string; months: MonthIndex[] } | null;
  bazi: BaziStrip | null;
  /** the level cut points the charts draw as bands (norms.cuts) */
  cuts: { decade: number[]; year: number[]; month: number[] } | null;
  norms: { version: string; kbVersion: string; charts: number; corpus: string } | null;
  method: Record<string, string>;
}

const zOf = (norms: IndexNorms | null, key: string, raw: number) => {
  const n = norms?.layers?.[key];
  return n ? r3((raw - n.mean) / (n.sd || 1)) : r3(raw);
};
/** Level 0 … 4 (index into LEVELS): how many cut points the score reaches. */
export function levelOf(score: number, cuts: number[] | undefined): number {
  return (cuts ?? FALLBACK_CUTS).filter(x => score >= x).length;
}
const part = (norms: IndexNorms | null, l: RawLayer, weight: number, key: string = l.layer): Part => {
  const z = zOf(norms, key, l.raw);
  return { layer: l.layer, raw: l.raw, z, weight, value: r3(weight * z), note: l.note, basis: l.basis };
};

/** The convention cap: the convention parts may add at most CONV_K × |sourced| (+ CONV_FLOOR when they agree with the books or the books
 *  are silent); against the books at most CONV_K × |sourced|, so the books' direction stands. Returns the correction part, or null. */
export function conventionCap(parts: Part[]): Part | null {
  const S = parts.filter(p => !CONVENTION.has(p.layer)).reduce((a, p) => a + p.value, 0);
  const C = parts.filter(p => CONVENTION.has(p.layer)).reduce((a, p) => a + p.value, 0);
  const agree = S === 0 || Math.sign(C) === Math.sign(S);
  const bound = CONV_K * Math.abs(S) + (agree ? CONV_FLOOR : 0);
  const capped = Math.max(-bound, Math.min(bound, C));
  if (Math.abs(capped - C) < 0.0005) return null;
  return { layer: 'thong_le_cap', raw: r3(C), z: r3(capped), weight: 1, value: r3(capped - C), basis: 'tinh_toan',
    note: `phần thông lệ ${vn(C)} giới hạn còn ${vn(capped)}: thông lệ chỉ ${agree ? 'nhấn thêm' : 'làm dịu'} chiều của sách (${vn(S)}), không lật được` };
}
/** Decade score without words: base = Σ weight × z with the convention cap; the robustness modifier then lifts or softens it. */
export function scoreDecade(norms: IndexNorms | null, layers: RawLayer[], vung: RawLayer): { score: number; parts: Part[] } {
  const parts = layers.map(l => part(norms, l, W_DECADE[l.layer as keyof typeof W_DECADE] ?? 0));
  const cap = conventionCap(parts);
  if (cap) parts.push(cap);
  const base = parts.reduce((a, p) => a + p.value, 0);
  const zv = zOf(norms, 'vung', vung.raw), r = Math.max(-VUNG_CLAMP, Math.min(VUNG_CLAMP, zv));
  const mod = r3(base * VUNG_GAIN * r * Math.sign(base));
  parts.push({ layer: 'vung', raw: vung.raw, z: zv, weight: VUNG_GAIN, value: mod, basis: vung.basis,
    note: `${vung.note}; hệ số ${vn(VUNG_GAIN)} × ${vn(r)} trên phần còn lại (${base >= 0 ? 'nâng' : 'đỡ'} khi lá số vững, ngược lại khi yếu)` });
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}
export function scoreYear(norms: IndexNorms | null, layers: RawLayer[], decadeScore: number | null): { score: number; parts: Part[] } {
  const parts: Part[] = [];
  if (decadeScore !== null) {
    const z = zOf(norms, 'dai_van', decadeScore);
    parts.push({ layer: 'dai_van', raw: decadeScore, z, weight: W_YEAR.dai_van, value: r3(W_YEAR.dai_van * z), basis: 'tinh_toan', note: 'mức của đại vận đang đi' });
  }
  for (const l of layers) parts.push(part(norms, l, W_YEAR[l.layer as keyof typeof W_YEAR] ?? 0, l.layer === 'luu_thai_tue' ? 'nen' : l.layer));
  const cap = conventionCap(parts);
  if (cap) parts.push(cap);
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}
export function scoreMonth(norms: IndexNorms | null, l: RawLayer, yearScore: number): { score: number; parts: Part[] } {
  const parts: Part[] = [{ layer: 'nam', raw: yearScore, z: yearScore, weight: 1, value: yearScore, basis: 'tinh_toan', note: 'mức của năm' }, part(norms, l, W_MONTH, 'nen')];
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}

/** Raw scores of every period of one chart, without words (tools/interpret/index_norms.ts uses it to place the cut points). */
export function periodScores(inp: PeriodInputs, norms: IndexNorms | null): { decades: number[]; years: number[]; months: number[] } {
  const decades = inp.decades.map(d => scoreDecade(norms, d.layers, inp.vung).score);
  const years = inp.years.map(y => scoreYear(norms, y.layers, y.decade === null ? null : decades[y.decade]).score);
  const i0 = inp.years.findIndex(y => y.year === inp.Y0);
  const ys = i0 >= 0 ? years[i0] : null;
  return { decades, years, months: ys === null || !inp.months ? [] : inp.months.map(m => scoreMonth(norms, m.layer, ys).score) };
}

// ================================================================ words ================================================================

const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : s;
const joinVi = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const bookTag = (it: Item) => it.book ? ` (${it.book}${it.basis === 'sach_dien_giai' ? ', diễn ý' : ''})` : '';
const topBy = (xs: Item[], side: Side, n: number) => {
  const seen = new Set<string>();
  return xs.filter(x => x.side === side && x.gist).sort((a, b) => b.w - a.w || (a.id < b.id ? -1 : 1)).filter(x => !seen.has(x.gist!) && !!seen.add(x.gist!)).slice(0, n);
};
/** "Theo sách về vận, A (Khảo Luận); B (Thực Hành); ngược lại, C (Toàn Thư, diễn ý)." — or '' when no book sentence fires. */
function bookSentence(items: Item[], lead: string): string {
  const pos = topBy(items, 'support', 2), neg = topBy(items, 'limit', pos.length ? 1 : 2);
  if (!pos.length && !neg.length) return '';
  const say = (xs: Item[]) => xs.map(x => `${x.gist}${bookTag(x)}`).join('; ');
  return `${lead} ${pos.length ? say(pos) : ''}${pos.length && neg.length ? '; ngược lại, ' : ''}${neg.length ? say(neg) : ''}.`;
}
/** "Hóa Quyền và Hóa Khoa vào ngay cung vận, Hóa Lộc vào Thiên Di (tam hợp)": names grouped by where they land, in first-seen order. */
function byPlace(xs: Item[], name: (i: Item) => string, home: string, verb: string): string {
  const g = new Map<string, string[]>();
  for (const i of xs) { const w = where(i, home); g.set(w, [...(g.get(w) ?? []), name(i)]); }
  return joinVi([...g.entries()].map(([w, ns]) => `${joinVi(ns)} ${verb} ${w}`));
}
const where = (it: Item, home: string) => it.scope === 'self' ? home : it.scope === 'menh' ? 'Mệnh' : `${it.palace} (${REL_VI[it.scope]})`;

function hoaSentence(items: Item[], stem: string, home: string, scopeWord: string): string {
  const good = items.filter(i => i.side === 'support').sort((a, b) => b.w - a.w), bad = items.filter(i => i.side === 'limit');
  const name = (i: Item) => i.text.split(' của ')[0];
  const goods = byPlace(good, name, home, 'vào'), bads = byPlace(bad, name, home, 'vào');
  if (!good.length && !bad.length) return `Tứ Hóa theo can ${stem} đều rơi ngoài tam phương ${scopeWord} và Mệnh, nên ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này ít chịu tác động của Tứ Hóa.`;
  if (good.length && bad.length) return `Theo thông lệ, can ${stem} đưa ${goods}, thêm lực cho ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này; nhưng ${bads}, kéo theo trở ngại ở đó.`;
  if (good.length) return `Theo thông lệ, can ${stem} đưa ${goods}, thêm lực cho ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này, còn Hóa Kỵ ở ngoài tầm.`;
  return `Theo thông lệ, can ${stem} đưa ${bads}, trong khi Lộc, Quyền, Khoa đều ngoài tầm, nên đây là điểm cần dè chừng.`;
}

function decadeText(d: DecadeFacts, y1: number, y2: number, parts: Part[], layers: RawLayer[], level: number): string[] {
  const out: string[] = [];
  const ev = d.kl?.event, dom = DOMAIN[d.palace];
  out.push(`Chặng ${d.age_from}–${d.age_to} tuổi (${y1}–${y2}) đi qua cung ${d.palace}${ev ? `, nên theo Khảo Luận biến cố của chặng thường liên quan đến ${ev}` : dom ? ` (cung của ${dom})` : ''}.`);
  out.push(hoaSentence(layers.find(l => l.layer === 'hoa_van')!.items, d.stem, 'ngay cung vận', 'cung vận'));
  const b = bookSentence(layers.find(l => l.layer === 'van')!.items, 'Sách về vận ghi:');
  if (b) out.push(b);
  const vung = parts.find(p => p.layer === 'vung')!, nen = parts.find(p => p.layer === 'nen')!;
  const base = parts.filter(p => p.layer !== 'vung').reduce((a, p) => a + p.value, 0);
  const tail = vung.z >= 0.75 ? `; lá số gốc vững hơn mức thường gặp nên ${base < 0 ? 'phần khó được đỡ bớt' : 'phần thuận dễ thành hơn'}`
    : vung.z <= -0.75 ? `; lá số gốc yếu hơn mức thường gặp nên ${base < 0 ? 'phần khó nặng thêm' : 'phần thuận khó giữ trọn'}`
    : Math.abs(nen.z) >= 1 ? (Math.sign(nen.z) === Math.sign(base) ? `; bản thân cung ${d.palace} ${nen.z > 0 ? 'vốn tốt' : 'vốn kém'} hơn mức thường gặp, nền ấy góp thêm`
      : `, dù bản thân cung ${d.palace} ${nen.z > 0 ? 'vốn tốt' : 'vốn kém'} hơn mức thường gặp`) : '';
  const soft = parts.some(p => p.layer === 'thong_le_cap' && Math.sign(p.value) === Math.sign(parts.filter(q => !CONVENTION.has(q.layer) && q.layer !== 'vung' && q.layer !== 'thong_le_cap').reduce((x, q) => x + q.value, 0)));
  out.push(`Tính chung, chặng này ở mức “${LEVELS[level]}” so với các chặng thường gặp${tail}${soft ? '; phần theo thông lệ chỉ làm dịu bớt, không đổi chiều của lời sách' : ''}.`);
  return out.map(cap);
}

function yearText(y: YearRaw, dec: DecadeIndex | null, level: number, parts: Part[]): string[] {
  const out: string[] = [];
  const dom = DOMAIN[y.palace];
  out.push(`Năm ${y.year} (${y.can_chi}), ${y.age} tuổi, ${dec ? `nằm trong chặng ${dec.age_from}–${dec.age_to} (cung ${dec.palace}, mức “${dec.level_vi}”)` : 'chưa vào đại vận đầu tiên'}; tiểu hạn ở cung ${y.palace}${dom ? ` (cung của ${dom})` : ''}.`);
  const thItems = y.layers.find(l => l.layer === 'tieu_han')!.items;
  // tiểu hạn in the đại vận's own palace: the decade panel already quotes the same sentences
  const b = dec && dec.palace === y.palace ? (thItems.length ? `Tiểu hạn trùng cung đại vận, nên những lời sách về cung ${y.palace} của chặng này được nhấn thêm trong năm.` : '')
    : bookSentence(thItems, 'Sách về vận ghi cho cung tiểu hạn:');
  if (b) out.push(b);
  const ls = [...y.layers.find(l => l.layer === 'luu_sao')!.items, ...y.layers.find(l => l.layer === 'luu_sao_tl')!.items], lh = y.layers.find(l => l.layer === 'luu_tu_hoa')!.items;
  const bits: string[] = [];
  const kh = ls.filter(i => (i.id === 'LUU_KHOC' || i.id === 'LUU_HU') && i.scope === 'self');
  const khNames = joinVi(kh.map(i => i.text.slice(4).split(' ở ')[0]));
  if (ls.some(i => i.id === 'TH_LUU_KHOC_HU_HUNG')) bits.push(`lưu ${khNames} gặp hung tinh ngay cung tiểu hạn, Thực Hành gọi là năm đầy tai ương, nước mắt`);
  else if (kh.length) bits.push(`lưu ${khNames} đến ngay cung tiểu hạn, Thực Hành coi là điềm xấu`);
  const others = ls.filter(i => !kh.includes(i) && i.id !== 'TH_LUU_KHOC_HU_HUNG');
  for (const side of ['limit', 'support'] as Side[]) {
    const xs = others.filter(i => i.side === side);
    if (xs.length) bits.push(`lưu ${byPlace(xs, i => i.text.slice(4).split(' ở ')[0], 'cung tiểu hạn', 'ở')}${side === 'limit' ? ' thêm sức cản' : ' thêm chút thuận'}`);
  }
  if (lh.length) bits.push(`theo thông lệ lưu Tứ Hóa, ${byPlace(lh, i => i.text.split(' của ')[0], 'cung tiểu hạn', 'vào')}`);
  if (bits.length) out.push(`${bits.slice(0, 3).join('; ')}.`);
  const lead = [...parts].sort((a, b) => Math.abs(b.value) - Math.abs(a.value))[0];
  const why = lead?.layer === 'dai_van' && Math.abs(lead.value) >= 0.2 ? `, phần lớn theo đà của đại vận đang đi`
    : lead && Math.abs(lead.value) >= 0.2 && lead.layer === 'tieu_han' ? `, phần lớn do cung tiểu hạn` : '';
  const soft = parts.some(p => p.layer === 'thong_le_cap' && Math.sign(p.value) === Math.sign(parts.filter(q => !CONVENTION.has(q.layer) && q.layer !== 'thong_le_cap').reduce((x, q) => x + q.value, 0)));
  out.push(`Tính chung năm ${y.year} ở mức “${LEVELS[level]}”${why}${soft ? '; phần theo thông lệ chỉ làm dịu bớt, không đổi chiều của lời sách' : ''}.`);
  return out.map(cap);
}

// ================================================================ Bát Tự strip ================================================================

const DH_TAG = { dung: 'Mang thần điều hậu (dụng)', hy: 'Mang thần điều hậu (hỷ)', khong: 'Không mang thần điều hậu' } as const;
function baziStrip(chart: ChartInput, Y0: number): BaziStrip | null {
  const b = chart.bazi, D = b?.deep;
  if (!b || !D?.luck?.length || !D.dieu_hau?.verified) return null;
  const luck = b.luck;
  const pillars = D.luck.map((l, i) => {
    const L = luck.find(x => x.name === l.pillar) ?? luck[l.index - 1];
    const roles = [l.dieu_hau?.stem, l.dieu_hau?.branch];
    const tag = roles.includes('yong') ? 'dung' : roles.includes('xi') ? 'hy' : 'khong';
    const next = D.luck[i + 1] && (luck.find(x => x.name === D.luck[i + 1].pillar) ?? luck[D.luck[i + 1].index - 1]);
    const yf = L?.start_year ?? null, yt = next?.start_year != null ? next.start_year - 1 : yf !== null ? yf + 9 : null;
    const red = l.findings.find(f => /DIEU_HAU/.test(f.rule_id));
    return { index: l.index, pillar: l.pillar, age_from: Math.round(L?.start_age ?? 0), year_from: yf, year_to: yt, tag: tag as 'dung' | 'hy' | 'khong', tag_vi: DH_TAG[tag],
      reduced: red ? red.text : null, current: yf !== null && yt !== null && yf <= Y0 && Y0 <= yt };
  });
  return { basis: 'Thiệu Vĩ Hoa tr.389-396 (bảng điều hậu)', cell: D.dieu_hau.cell, pillars,
    note: 'Bảng điều hậu chỉ ghi thần cần dùng; vận không mang thần ấy được để trống, không gọi là kỵ. Dải này đặt cạnh để đối chiếu, không cộng vào mức Tử Vi.' };
}

// ================================================================ all indices ================================================================

/** All indices for one chart; `year` is the facts' viewed year (facts.year.year). Deterministic: same facts, knowledge and norms → same output. */
export function computeIndices(chart: ChartInput, k: Knowledge, norms: IndexNorms | null, span = 10): Indices {
  const inp = periodInputs(chart, k, norms, span);
  const Y0 = chart.year.year, born = chart.lunar_year, cur = chart.year.dai_han;
  const decades: DecadeIndex[] = inp.decades.map(({ d, layers }) => {
    const { score, parts } = scoreDecade(norms, layers, inp.vung);
    const level = levelOf(score, norms?.cuts?.decade);
    const y1 = born + d.age_from - 1, y2 = born + d.age_to - 1;
    return { index: d.index, palace: d.palace, branch: d.branch, stem: d.stem, age_from: d.age_from, age_to: d.age_to, year_from: y1, year_to: y2,
      current: !!cur && cur.age_from === d.age_from, score, level, level_vi: LEVELS[level], parts,
      items: layers.flatMap(l => l.items), text: decadeText(d, y1, y2, parts, layers, level) };
  });
  const years: YearIndex[] = inp.years.map(y => {
    const dec = y.decade === null ? null : decades[y.decade];
    const { score, parts } = scoreYear(norms, y.layers, dec ? dec.score : null);
    const level = levelOf(score, norms?.cuts?.year);
    return { year: y.year, age: y.age, can_chi: y.can_chi, palace: y.palace, branch: y.branch, thai_tue: y.thai_tue, current: y.year === Y0, decade: y.decade,
      score, level, level_vi: LEVELS[level], parts, items: y.layers.flatMap(l => l.items), text: yearText(y, dec, level, parts) };
  });
  const yv = years.find(y => y.current);
  const months = inp.months && yv ? { year: Y0, basis: 'TH tr.115 (vị trí tháng); mức của tháng = mức của năm, nhích theo chất lượng bẩm sinh của cung nguyệt hạn',
    months: inp.months.map(m => {
      const { score, parts } = scoreMonth(norms, m.layer, yv.score);
      const level = levelOf(score, norms?.cuts?.month);
      const z = parts[1].z;
      return { month: m.month, palace: m.palace, score, level, level_vi: LEVELS[level], parts, items: [],
        text: [`Tháng ${m.month} âm lịch rơi vào cung ${m.palace} (Thực Hành tr.115)${DOMAIN[m.palace] ? `, cung của ${DOMAIN[m.palace]}` : ''}; đây chỉ là vị trí tháng, nên mức của tháng là mức của năm ${Y0}${Math.abs(z) >= 0.5 ? `, ${z > 0 ? 'nhích lên' : 'nhích xuống'} một chút theo cung này` : ''}: “${LEVELS[level]}”.`] };
    }) } : null;

  return {
    version: INDICES_VERSION, disclaimer: DISCLAIMER, year: Y0, levels: LEVELS, palaces: inp.palaces, decades, years, months, bazi: baziStrip(chart, Y0), cuts: norms?.cuts ?? null,
    norms: norms && { version: norms.version, kbVersion: norms.kbVersion, charts: norms.charts, corpus: norms.corpus },
    method: {
      thang: `mỗi lớp là một giá trị thô (bên thuận trừ bên bất lợi), quy về điểm chuẩn so với ${norms?.charts ?? 1000} lá số mẫu rồi cộng theo trọng số; năm mức lấy theo các ngưỡng 12 / 33 / 67 / 88 % của chính loại giai đoạn ấy trên bộ mẫu (quy ước hệ thống)`,
      sach_truoc: `lớp có sách quyết định chiều; các lớp thông lệ cộng lại chỉ được thêm tối đa ${vn(CONV_K)} × phần có sách (+ ${vn(CONV_FLOOR)} khi cùng chiều hoặc sách không nói), nên không lật được lời sách`,
      dai_van: `câu sách về cung vận ${vn(W_DECADE.van)} (Khảo Luận tr.230-236, Thực Hành tr.115-117; Toàn Thư tr.97-105 diễn ý × ${vn(TT_WEIGHT)}), nền bẩm sinh của cung vận ${vn(W_DECADE.nen)}, Tứ Hóa theo can đại vận ${vn(W_DECADE.hoa_van)} (thông lệ); rồi hệ số độ vững của Mệnh và tam phương ± ${vn(VUNG_GAIN)} × điểm chuẩn (giới hạn ${vn(VUNG_CLAMP)})`,
      nam: `đại vận đang đi ${vn(W_YEAR.dai_van)}, câu sách về cung tiểu hạn ${vn(W_YEAR.tieu_han)}, nền bẩm sinh cung tiểu hạn ${vn(W_YEAR.nen)}, lưu Khốc Hư ở tiểu hạn ${vn(W_YEAR.luu_sao)} (TH tr.114); thông lệ: cung lưu Thái Tuế ${vn(W_YEAR.luu_thai_tue)}, các sao lưu khác ${vn(W_YEAR.luu_sao_tl)} (vị trí KL tr.41-42), lưu Tứ Hóa ${vn(W_YEAR.luu_tu_hoa)}`,
      thang_am: `mức của năm cộng ${vn(W_MONTH)} × điểm chuẩn chất lượng bẩm sinh của cung nguyệt hạn (vị trí TH tr.115)`,
      ban_menh: 'mười hai cung: nhận định đã đối chiếu sách bắn vào cung, cung xung chiếu và hai cung tam hợp; trọng số = tầng × (0,5 + độ hiếm của quy tắc trên chính cung đó) × vị trí (1 / 0,85 / 0,7); so với trung bình của chính cung đó: (tổng + 1) / (trung bình + 1)',
      bat_tu: 'dải Bát Tự: vận nào mang can hoặc chi thuộc thần điều hậu của bảng Thiệu Vĩ Hoa (tr.389-396); không cộng vào mức Tử Vi',
    },
  };
}
