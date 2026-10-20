// Structures for the reasoner (plan quirky-tinkering-rabin R2): what the chart's dominant structure is, so prose can name it.
//   (a) evaluateFormations — port of engine/tvbt/reasoning/formation_eval.py (evaluate_formation + render_vi) over the ten experimental
//       cách cục of engine/data/experimental/formations_experimental.json. Python runs them before any rule, on base facts only (chart facts
//       + the anchor palace's facts, nothing derived), and so does this port. Every formation is draft/experimental; none is ever verified.
//   (b) detectStructures — port of engine/tvbt/synthesis/structures.py (detect_all): six chart-agnostic detectors with premises, supports,
//       limiters, rescuers, school variants, the cited pages and an honest verification level. Vietnamese strings are verbatim.
//   (c) labelledFindings — the fired rules that name a cách or a grouping (kg/lift.ts `labelled`), for the same evidence panel.
// Parity with Python over the 1,000-chart corpus: test/structures.test.ts against tools/interpret/make_structure_parity.py.
import { evaluate, type World } from '../dsl.ts';
import { lift, type Labelled } from '../kg/lift.ts';
import type { Expr, Facts, Finding, Knowledge, Palace, Tri } from '../types.ts';

// ---------------------------------------------------------------- (a) formations

export type FormationState = 'khong_hien' | 'hinh_thuc' | 'thanh' | 'thanh_thuong' | 'bi_pha' | 'pha_duoc_cuu' | 'chua_du_du_kien';
export interface Evidence { id: string; label: string; when: Expr; rescues?: string[] }
/** One entry of formations_experimental.json (engine/tvbt/knowledge/formation.py Formation). */
export interface Formation {
  id: string; name_vi: string; anchor: string; core: Expr; kind?: string; school?: string;
  boosters?: Evidence[]; breakers?: Evidence[]; rescuers?: Evidence[]; refutations?: Evidence[]; thuong_at?: number;
  sourceIds?: string[]; reviewStatus: 'draft' | 'disputed' | 'verified'; experimental?: boolean; provenance?: string; note?: string; definition_version?: number;
}
type EvKind = 'boosters' | 'breakers' | 'rescuers' | 'refutations';

/** formation_eval.evaluate_formation's dict, field for field (snake_case kept so it compares with the Python fixture directly). */
export interface FormationVerdict {
  id: string; name_vi: string; anchor: string; core: Tri; state: FormationState;
  boosters: string[]; breakers: string[]; rescuers: string[]; refutations: string[]; uncovered_breakers: string[]; unknown: string[];
  missing_for_next_level: string[]; downgraded_by_refutation: boolean; caveats: string[];
}
export interface MatchedEvidence { id: string; label: string }
/** What the reasoner reads: the verdict plus the matched evidence with its labels, the Vietnamese sentence and the review level. */
export interface FormationResult {
  id: string; name: string; anchor: string; kind: string; state: FormationState; stateVi: string; effect: 'support' | 'limit' | 'neutral';
  boosters: MatchedEvidence[]; breakers: MatchedEvidence[]; rescuers: MatchedEvidence[]; refutations: MatchedEvidence[]; uncovered: MatchedEvidence[];
  missing: string[]; downgraded: boolean; caveats: string[]; text: string;
  /** reviewStatus of the definition: 'draft' for all ten (formation.py refuses 'verified'); experimental definitions are never production rules */
  verification: Formation['reviewStatus']; experimental: boolean;
  verdict: FormationVerdict;
}

export const EFFECT: Record<FormationState, 'support' | 'limit' | 'neutral'> = { thanh: 'support', thanh_thuong: 'support', bi_pha: 'limit', hinh_thuc: 'neutral',
  pha_duoc_cuu: 'neutral', khong_hien: 'neutral', chua_du_du_kien: 'neutral' };
export const STATE_VI: Record<FormationState, string> = { khong_hien: 'không hiện', hinh_thuc: 'chỉ có hình thức', thanh: 'thành cách', thanh_thuong: 'thành cách, thế mạnh',
  bi_pha: 'bị phá cách', pha_duoc_cuu: 'bị phá nhưng được cứu giải', chua_du_du_kien: 'chưa đủ dữ kiện' };
const LOWER: Partial<Record<FormationState, FormationState>> = { thanh_thuong: 'thanh', thanh: 'hinh_thuc' };

const ev = (f: Formation, kind: EvKind): Evidence[] => f[kind] ?? [];

/** Port of evaluate_formation: the state follows the fixed order of formation_eval.py (core → uncovered breaker → rescued → booster count,
 *  then a refutation lowers thành by one rung). An UNKNOWN sub-condition is reported, never counted as false. */
export function evaluateFormation(f: Formation, facts: Facts, world?: World): FormationVerdict {
  const core = evaluate(f.core, facts, world);
  const d: FormationVerdict = { id: f.id, name_vi: f.name_vi, anchor: f.anchor, core, state: 'khong_hien', boosters: [], breakers: [], rescuers: [],
    refutations: [], uncovered_breakers: [], unknown: [], missing_for_next_level: [], downgraded_by_refutation: false, caveats: [] };
  if (core !== true) {
    d.state = core === false ? 'khong_hien' : 'chua_du_du_kien';
    if (core === null) d.caveats.push('điều kiện lõi thiếu dữ kiện');
    return d;
  }
  const unknownLabels: string[] = [];
  const active = (kind: EvKind): Evidence[] => {
    const out: Evidence[] = [];
    for (const e of ev(f, kind)) {
      const v = evaluate(e.when, facts, world);
      if (v === true) out.push(e);
      else if (v === null) { d.unknown.push(`${kind}:${e.id}`); unknownLabels.push(e.label); }
    }
    return out;
  };
  const boosters = active('boosters'), breakers = active('breakers'), rescuers = active('rescuers'), refs = active('refutations');
  const covered = new Set<string>();
  for (const r of rescuers) for (const id of (r.rescues ?? []).includes('*') ? ev(f, 'breakers').map(b => b.id) : (r.rescues ?? [])) covered.add(id);
  const uncovered = breakers.filter(b => !covered.has(b.id));
  Object.assign(d, { boosters: boosters.map(e => e.id), breakers: breakers.map(e => e.id), rescuers: rescuers.map(e => e.id),
    refutations: refs.map(e => e.id), uncovered_breakers: uncovered.map(b => b.id) });
  let state: FormationState;
  if (uncovered.length) {
    state = 'bi_pha';
    const ub = new Set(uncovered.map(b => b.id));
    const usable = ev(f, 'rescuers').filter(r => !rescuers.includes(r) && ((r.rescues ?? []).includes('*') || (r.rescues ?? []).some(x => ub.has(x))));
    d.missing_for_next_level = usable.map(r => `cứu giải: ${r.label}`);
  } else if (breakers.length) {
    state = 'pha_duoc_cuu';
  } else {
    const n = boosters.length;
    state = n >= (f.thuong_at ?? 2) ? 'thanh_thuong' : n >= 1 ? 'thanh' : 'hinh_thuc';
    const left = ev(f, 'boosters').filter(e => !boosters.includes(e)).map(e => e.label);
    if (state === 'hinh_thuc' || state === 'thanh') d.missing_for_next_level = left.map(x => `tăng thế: ${x}`);
    const lower = LOWER[state];
    if (refs.length && lower) { state = lower; d.downgraded_by_refutation = true; }
  }
  if (d.unknown.length) d.caveats.push('có điều kiện chưa đủ dữ kiện nên không được tính là sai: ' + unknownLabels.join('; '));
  d.state = state;
  return d;
}

function labels(f: Formation, kind: EvKind, ids: string[]): string {
  const m = new Map(ev(f, kind).map(e => [e.id, e.label]));
  return ids.map(i => m.get(i)!).join('; ');
}

/** Port of render_vi: deterministic Vietnamese description of one verdict; states what the structure contains, asserts no event. */
export function renderFormationVi(f: Formation, d: FormationVerdict): string {
  let s = `Cách ${f.name_vi} (cung ${f.anchor}): ${STATE_VI[d.state]}.`;
  if (d.state === 'khong_hien' || d.state === 'chua_du_du_kien') return s;
  if (d.boosters.length) s += ` Yếu tố tăng thế: ${labels(f, 'boosters', d.boosters)}.`;
  if (d.breakers.length) s += ` Yếu tố phá cách: ${labels(f, 'breakers', d.breakers)}.`;
  if (d.rescuers.length) s += ` Yếu tố cứu giải: ${labels(f, 'rescuers', d.rescuers)}.`;
  if (d.uncovered_breakers.length) s += ` Chưa có yếu tố nào cứu: ${labels(f, 'breakers', d.uncovered_breakers)}.`;
  if (d.refutations.length) s += ` Phản chứng cần xét: ${labels(f, 'refutations', d.refutations)}` + (d.downgraded_by_refutation ? ' (vì vậy hạ một bậc).' : '.');
  if (d.missing_for_next_level.length) s += ' Còn thiếu: ' + d.missing_for_next_level.join('; ') + '.';
  for (const c of d.caveats) s += ` Lưu ý: ${c}.`;
  return s + ' (Bản thử nghiệm, chưa đối chiếu sách; chỉ mô tả cấu trúc, không dự báo.)';
}

/** Every formation at its anchor palace, on base facts (chart facts + that palace's facts), as engine.py's run_formations does before the
 *  rule loop. A formation whose anchor palace is not in the base is skipped, as in Python. */
export function evaluateFormations(formations: Formation[], base: Record<string, Facts>): FormationResult[] {
  const factsOf = (subj: string): Facts => ({ ...(base.chart ?? {}), ...base[subj] });
  const world: World = n => base[`palace:${n}`] ? factsOf(`palace:${n}`) : null;
  const out: FormationResult[] = [];
  for (const f of formations) {
    const subj = `palace:${f.anchor}`;
    if (!(subj in base)) continue;
    const d = evaluateFormation(f, factsOf(subj), world);
    const pick = (kind: EvKind, ids: string[]): MatchedEvidence[] => { const m = new Map(ev(f, kind).map(e => [e.id, e.label])); return ids.map(id => ({ id, label: m.get(id)! })); };
    out.push({ id: f.id, name: f.name_vi, anchor: f.anchor, kind: f.kind ?? 'cat', state: d.state, stateVi: STATE_VI[d.state], effect: EFFECT[d.state],
      boosters: pick('boosters', d.boosters), breakers: pick('breakers', d.breakers), rescuers: pick('rescuers', d.rescuers),
      refutations: pick('refutations', d.refutations), uncovered: pick('breakers', d.uncovered_breakers),
      missing: d.missing_for_next_level, downgraded: d.downgraded_by_refutation, caveats: d.caveats, text: renderFormationVi(f, d),
      verification: f.reviewStatus, experimental: f.experimental ?? true, verdict: d });
  }
  return out;
}

// ---------------------------------------------------------------- (b) special structures

export type Verification = 'da_doi_chieu' | 'mot_phan' | 'chua_du_nguon';
/** structures.py Structure, field for field. */
export interface Structure {
  id: string; name: string; palaces: string[]; present: boolean;
  premises: Array<{ text: string; ok: boolean }>; supports: string[]; limiters: string[]; rescuers: string[];
  variants: Array<Record<string, unknown>>; cites: string[]; verification: Verification; matrix_ids: string[]; reading: string; caveat: string;
}

export const SAT = ['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp'];
export const CAT = ['Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc', 'Thiên Khôi', 'Thiên Việt'];
const TU_MO = ['Thìn', 'Tuất', 'Sửu', 'Mùi'];
type TuHoa = Record<string, { star: string; branch: number }>;

function structure(id: string, name: string, palaces: string[], present: boolean): Structure {
  return { id, name, palaces, present, premises: [], supports: [], limiters: [], rescuers: [], variants: [], cites: [], verification: 'chua_du_nguon',
    matrix_ids: [], reading: '', caveat: '' };
}
/** Python sorted() on str: code-point order (every string here is in the BMP, so UTF-16 order is the same). */
const sorted = (xs: Iterable<string>): string[] => [...xs].sort((a, b) => a < b ? -1 : a > b ? 1 : 0);
const uniqSorted = (xs: string[]): string[] => sorted(new Set(xs));

class Geo {
  readonly ps = new Map<string, Palace>(); readonly byB = new Map<number, Palace>(); readonly hoa: TuHoa;
  constructor(palaces: Palace[], hoa: TuHoa) {
    this.hoa = hoa;
    for (const p of palaces) { this.ps.set(p.name, p); this.byB.set(p.branch_index, p); }
  }
  opp(p: Palace): Palace { return this.byB.get((p.branch_index + 6) % 12)!; }
  tamHop(p: Palace): Palace[] { return [4, 8].map(d => this.byB.get((p.branch_index + d) % 12)!); }
  scope(p: Palace, kind: 'dong_cung' | 'doi_cung' | 'tam_phuong' = 'tam_phuong'): Palace[] {
    if (kind === 'dong_cung') return [p];
    if (kind === 'doi_cung') return [p, this.opp(p)];
    return [p, this.opp(p), ...this.tamHop(p)];
  }
  stars(ps: Palace[]): string[] { return ps.flatMap(p => p.stars); }
  hoaIn(ps: Palace[]): string[] { const br = new Set(ps.map(p => p.branch_index)); return sorted(Object.entries(this.hoa).filter(([, v]) => br.has(v.branch)).map(([k]) => k)); }
}

const tt = (p: Palace): string => (p.tuan ? 'Tuần' : '') + (p.tuan && p.triet ? ' và ' : '') + (p.triet ? 'Triệt' : '');

function cuMonHamHoaLoc(g: Geo): Structure {
  const p = [...g.ps.values()].find(q => q.major_stars.includes('Cự Môn'));
  const loc = g.hoa['Hóa Lộc'];
  if (!p || loc?.star !== 'Cự Môn') return structure('CU_MON_HOA_LOC', 'Cự Môn hóa Lộc', [], false);
  const dig = p.major_dignity['Cự Môn'] ?? 'chưa rõ';
  const ham = dig === 'hãm';
  const sc = g.scope(p);
  const sat = g.stars(sc).filter(s => SAT.includes(s));
  const ky = g.hoaIn(sc).includes('Hóa Kỵ');
  const s = structure('CU_MON_HOA_LOC', 'Cự Môn ' + dig + ' gặp Hóa Lộc', [p.name], true);
  s.premises = [{ text: `Cự Môn tại ${p.branch} (${p.name}), độ sáng: ${dig}`, ok: true },
    { text: 'Cự Môn bị hãm — điều kiện để áp dụng cách đọc ‘hãm gặp Lộc’', ok: ham },
    { text: 'Hóa Lộc rơi đúng vào Cự Môn (Lộc đồng cung với sao hóa)', ok: true }];
  s.supports = ['Hóa Lộc gắn vào chính Cự Môn: sao hóa luôn thuộc sao gốc, nên Lộc bổ sung phần ‘lợi’ cho tính chất của Cự Môn (lời nói, thị phi, việc ngầm) hơn là xóa độ sáng'];
  if (p.branch === 'Tý' || p.branch === 'Ngọ') {
    s.supports.push('Cự Môn ở Tý/Ngọ: một số định nghĩa ‘Thạch trung ẩn ngọc’ coi Tuần/Triệt hoặc Hóa Lộc là điều kiện thành cách (KL tr.106, TH tr.43) — nhưng các định nghĩa khác nhau (R08)');
    s.matrix_ids.push('R08');
  }
  if (TU_MO.includes(p.branch)) s.limiters.push('Hóa Lộc đóng ở Tứ Mộ: tài lộc giảm nhiều (KL tr.66; TH tr.52 nói giảm quá nửa, trừ khi gặp Tham/Vũ)');
  if (sat.length) s.limiters.push('Sát tinh trong tam phương tứ chính: ' + uniqSorted(sat).join(', '));
  if (ky) s.limiters.push('Hóa Kỵ cũng nằm trong tam phương tứ chính (theo bảng Tứ Hóa đang dùng)');
  if (p.tuan || p.triet) {
    s.rescuers.push(`Cung có ${tt(p)}: sách có hai chiều (hại quý tinh / cứu hung tinh / kỳ cách với Cự Môn Tý Ngọ) — R07, không tự chọn`);
    s.matrix_ids.push('R07');
  }
  s.cites = ['KL tr.66', 'TH tr.52', 'KL tr.106', 'TH tr.43'];
  s.verification = 'mot_phan';
  s.reading = 'Điều kiện tiên quyết ‘Cự Môn hãm’ ' + (ham ? 'đúng' : 'KHÔNG đúng (độ sáng: ' + dig + '), nên không áp dụng cách đọc ‘hãm gặp Lộc’') +
    '. Sách trong bộ quy tắc không có câu nói thẳng ‘Cự Môn hãm gặp Hóa Lộc’; hệ thống chỉ ghép các thành phần có câu sách (Hóa Lộc ở Tứ Mộ, Tuần/Triệt, Cự Môn Tý Ngọ). ' +
    'Vì vậy kết luận mang tính điều kiện: Lộc cho thêm cơ hội về tài/danh qua lời nói và quan hệ, còn mức độ phát huy phụ thuộc vào sát tinh, Kỵ và Tuần/Triệt kể trên.';
  s.caveat = 'Chưa có nguồn cho tổ hợp này; không được đọc thành ‘hãm biến thành tốt’.';
  return s;
}

function tamHoaHoiMenh(g: Geo): Structure {
  const m = g.ps.get('Mệnh')!;
  const kinds = ['dong_cung', 'doi_cung', 'tam_phuong'] as const;
  const res = Object.fromEntries(kinds.map(k => [k, g.hoaIn(g.scope(m, k)).filter(h => h === 'Hóa Lộc' || h === 'Hóa Quyền' || h === 'Hóa Khoa')])) as Record<typeof kinds[number], string[]>;
  const three = (v: string[]) => new Set(v).size === 3;
  const full = three(res.tam_phuong);
  const s = structure('TAM_HOA_HOI_MENH', 'Tam Hóa (Lộc–Quyền–Khoa) hội Mệnh', ['Mệnh'], full);
  s.premises = kinds.map(k => ({ text: `Phạm vi ${k.replaceAll('_', ' ')}: ` + (res[k].join(', ') || 'không có'), ok: three(res[k]) }));
  if (!full) return s;
  const ky = g.hoaIn(g.scope(m)).includes('Hóa Kỵ');
  const sat = g.stars(g.scope(m)).filter(x => SAT.includes(x));
  s.supports = ['Ba hóa Lộc, Quyền, Khoa cùng chiếu về Mệnh trong tam phương tứ chính (TH tr.87 — tiếng tăm về văn chương, học vấn; TH tr.30–33 nêu Tam Hóa là một trong các cát tinh làm tăng thế chính tinh)'];
  if (ky) s.limiters.push('Hóa Kỵ cũng nằm trong tam phương: bốn hóa tề tụ; sách trích không phân xử trường hợp này');
  if (sat.length) s.limiters.push('Sát tinh trong tam phương: ' + uniqSorted(sat).join(', '));
  if (!res.dong_cung.length && !res.doi_cung.length) {
    s.limiters.push('Cả ba hóa chỉ đến từ hai cung tam hợp; nếu hiểu ‘hội’ hẹp hơn thì nhận định không còn đủ ba (R01)');
    s.matrix_ids.push('R01');
  }
  s.variants = kinds.map(k => ({ scope: k, holds: three(res[k]), found: res[k] }));
  s.cites = ['TH tr.87', 'TH tr.30', 'TH tr.31', 'TH tr.33'];
  s.verification = 'da_doi_chieu';
  if (!s.matrix_ids.includes('R01')) s.matrix_ids.push('R01');
  s.reading = 'Tam Hóa hội Mệnh là điều kiện làm tăng thế của chính tinh tại Mệnh, không phải kết quả độc lập: giá trị đọc phải đi qua độ sáng của chính tinh chứa các hóa và qua việc sát tinh/Kỵ có cùng hội hay không.';
  s.caveat = 'Chữ ‘hội’ không nêu phạm vi trong sách; kết quả được báo theo ba phạm vi.';
  return s;
}

function thanCuQuanLocVcd(g: Geo): Structure {
  const q = g.ps.get('Quan Lộc')!;
  const than = [...g.ps.values()].find(p => p.is_than);
  const thanQuan = !!than && than.name === 'Quan Lộc';
  const present = thanQuan && !q.major_stars.length;
  const s = structure('THAN_QUAN_VCD', 'Thân cư Quan Lộc vô chính diệu', ['Quan Lộc'], present);
  s.premises = [{ text: 'Thân cư Quan Lộc', ok: thanQuan }, { text: 'Quan Lộc không có chính tinh', ok: !q.major_stars.length }];
  if (!present) return s;
  const o = g.opp(q);
  s.supports = ['Mượn chính tinh cung đối (Phu Thê): ' + (o.major_stars.join(', ') || 'đối cung cũng không có chính tinh') + ' — chỉ là cách đọc phụ trợ theo thói quen'];
  const other = g.stars(g.tamHop(q)).filter(x => SAT.includes(x) || CAT.includes(x));
  if (other.length) s.supports.push('Phụ tinh ở hai cung tam hợp: ' + uniqSorted(other).join(', '));
  if (q.tuan || q.triet) s.limiters.push(`Quan Lộc có ${tt(q)}; sách chỉ bàn Tuần/Triệt ở Mệnh vô chính diệu (TH tr.53, bản nháp), không bàn riêng ở Quan Lộc`);
  s.cites = ['KL tr.222 (Mệnh vô chính diệu — không áp cho Quan Lộc)', 'KL tr.218 (Thiên Di vô chính diệu — không áp cho Quan Lộc)'];
  s.verification = 'chua_du_nguon';
  s.matrix_ids = [];
  s.reading = 'Hệ thống không có câu sách cho ‘Thân cư Quan Lộc vô chính diệu’. Điều rõ từ vị trí: nghề nghiệp/công danh là trọng tâm đời sống của chủ thể (Thân ở đó) và cung không tự có chính tinh nên tính chất do cung đối và tam hợp quyết định. ' +
    'Việc mượn sao đối cung chỉ là phép đọc phụ trợ của một số trường phái, không phải quy tắc đã xác minh; không dùng để kết luận mức thành bại.';
  s.caveat = 'Không suy diễn vượt nguồn (U_THAN_QUAN_VCD).';
  return s;
}

function coNguyetPhuThe(g: Geo): Structure {
  const p = g.ps.get('Phu Thê')!;
  const co = p.major_stars.includes('Thiên Cơ'), am = p.major_stars.includes('Thái Âm');
  const present = co || am;
  const s = structure('CO_NGUYET_PHU_THE', 'Cơ / Nguyệt tại Phu Thê' + (co && am ? ' đồng cung' : ''), ['Phu Thê'], present);
  s.premises = [{ text: 'Thiên Cơ ở Phu Thê', ok: co }, { text: 'Thái Âm ở Phu Thê', ok: am }];
  if (!present) return s;
  const sc = g.scope(p);
  const hoaHere = g.hoaIn([p]);
  const da = p.stars.includes('Đà La'), daSc = g.stars(sc).includes('Đà La');
  const ky = hoaHere.includes('Hóa Kỵ'), kySc = g.hoaIn(sc).includes('Hóa Kỵ');
  s.supports = ['Sách tả người phối ngẫu và tuổi kết hôn theo sao ở Phu Thê (TT tr.82–83; KL tr.80 cho Thiên Cơ ở Tỵ/Ngọ/Mùi)'];
  for (const [flag, txt] of [[p.tuan || p.triet, `Cung có ${tt(p)}`], [ky, 'Hóa Kỵ đồng cung'], [da, 'Đà La đồng cung']] as Array<[boolean, string]>) if (flag) s.limiters.push(txt);
  if (!ky && kySc) s.limiters.push('Hóa Kỵ trong tam phương tứ chính (không đồng cung)');
  if (!da && daSc) s.limiters.push('Đà La trong tam phương tứ chính (không đồng cung)');
  if (p.tuan || p.triet) s.matrix_ids.push('R07');
  s.cites = ['TT tr.82–83', 'KL tr.80'];
  s.verification = 'mot_phan';
  s.reading = 'Phần ‘sao nào ở Phu Thê’ có câu sách; phần ‘gặp Tuần/Kỵ/Đà’ chỉ có các câu chung về hung tinh/Tuần/Triệt (R07) chứ không có câu riêng cho Cơ Nguyệt ở Phu Thê. ' +
    'Do đó điều được nói là: đặc điểm tuổi tác/tính cách người phối ngẫu theo sao, cộng thêm các yếu tố có thể làm quan hệ khó ổn định hoặc chậm; không kết luận về thành bại hôn nhân.';
  s.caveat = 'Nhận định truyền thống về hôn nhân không phải dự báo.';
  return s;
}

function kinhDuongTuMo(g: Geo): Structure[] {
  const out: Structure[] = [];
  for (const p of g.ps.values()) {
    if (!(p.stars.includes('Kình Dương') && TU_MO.includes(p.branch))) continue;
    const s = structure('KINH_DUONG_TU_MO', `Kình Dương ở Tứ Mộ (${p.branch}) — cung ${p.name}`, [p.name], true);
    const dig = p.minor_dignity['Kình Dương'] || 'chưa rõ';
    const sc = g.scope(p);
    const hoa = p.stars.includes('Hỏa Tinh');
    const bad = g.stars(sc).filter(x => ['Địa Không', 'Địa Kiếp', 'Linh Tinh', 'Đà La'].includes(x));
    s.premises = [{ text: `Kình Dương tại ${p.branch}, độ sáng: ${dig}`, ok: true }, { text: 'Đồng cung Hỏa Tinh', ok: hoa }];
    if (hoa) s.supports.push('Kình Dương đồng cung Hỏa Tinh ở Tứ Mộ: uy quyền lớn (TT tr.50, nói riêng về cung Mệnh)');
    const kq = g.hoaIn(sc).filter(x => x === 'Hóa Quyền' || x === 'Hóa Khoa' || x === 'Hóa Lộc');
    if (kq.length) {
      s.rescuers.push('Có ' + kq.join(', ') + ' trong tam phương (KL tr.64 nêu ‘Kình gặp Khoa Quyền Lộc’ là thế tốt — với điều kiện xa Thất Sát/Thiên Hình)');
      s.matrix_ids.push('R08');
    }
    if (bad.length) s.limiters.push('Sát tinh khác trong tam phương: ' + uniqSorted(bad).join(', '));
    if (p.stars.some(x => x === 'Thất Sát' || x === 'Thiên Hình')) s.limiters.push('Đồng cung Thất Sát/Thiên Hình: trong định nghĩa của TT tr.142 (Kình ở Ngọ) là thế xấu; ở Tứ Mộ không có câu tương ứng');
    s.cites = ['TT tr.50', 'KL tr.64', 'TT tr.142'];
    s.verification = p.name === 'Mệnh' ? 'mot_phan' : 'chua_du_nguon';
    s.reading = 'Tứ Mộ là nơi Kình Dương được xếp ở thế dễ dùng được (sức mạnh, quyết đoán), nhưng quy tắc trong bộ sách chỉ nêu rõ cho cung Mệnh có Hỏa Tinh. ' +
      (p.name !== 'Mệnh' ? 'Cung này không phải Mệnh nên chỉ ghi vị trí và các yếu tố đi kèm.' : 'Kết luận phụ thuộc Hỏa Tinh, Khoa–Quyền–Lộc và các sát tinh còn lại.');
    out.push(s);
  }
  return out;
}

function satPhaTham(g: Geo): Structure {
  const m = g.ps.get('Mệnh')!;
  const sc = g.scope(m);
  const stars = g.stars(sc);
  const majors = sc.flatMap(p => p.major_stars);
  const three = ['Thất Sát', 'Phá Quân', 'Tham Lang'];
  const spt = three.filter(x => majors.includes(x));
  const present = spt.length === 3;
  const s = structure('SAT_PHA_THAM', 'Sát – Phá – Tham trong tam phương Mệnh', ['Mệnh'], present);
  s.premises = three.map(x => ({ text: `${x} trong tam phương tứ chính của Mệnh`, ok: spt.includes(x) }));
  if (!present) return s;
  const sat = uniqSorted(stars.filter(x => SAT.includes(x)));
  const cat = uniqSorted(stars.filter(x => CAT.includes(x)));
  const ky = g.hoaIn(sc).includes('Hóa Kỵ');
  const gp = [{ threshold: '≥1 sát tinh', breaks: sat.length >= 1 }, { threshold: '≥2 sát tinh', breaks: sat.length >= 2 },
    { threshold: '≥3 sát tinh và Kỵ (quy ước thiết kế)', breaks: sat.length >= 3 && ky }];
  s.variants = gp;
  s.supports = ['Cát tinh trong tam phương: ' + (cat.length ? cat.join(', ') : 'không có')];
  s.limiters = ['Sát tinh trong tam phương: ' + (sat.length ? sat.join(', ') : 'không có'), ...(ky ? ['Hóa Kỵ trong tam phương'] : [])];
  s.matrix_ids.push('R03', 'R01');
  const verdicts = new Set(gp.map(v => v.breaks));
  s.cites = ['TH tr.77', 'TH tr.116'];
  s.verification = 'mot_phan';
  s.reading = 'Thế Sát–Phá–Tham là thế biến động, ‘làm nên’ hay ‘lao đao’ tùy cát/sát đi kèm (TH tr.77). ' +
    (verdicts.size > 1 ? 'Ba ngưỡng sát tinh trong sách cho ba kết luận khác nhau về việc có bị phá cách hay không — phải trình bày cả ba.' :
      'Với dữ liệu này cả ba ngưỡng đều cho cùng kết luận ' + (verdicts.has(true) ? '‘phá cách’.' : '‘không phá cách’.'));
  s.caveat = 'Ngưỡng phá cách chưa đủ nguồn (R03).';
  return s;
}

/** Port of detect_all: every detector, present or not, in Python's order (Kình Dương Tứ Mộ: one entry per palace that has it). */
export function detectStructures(palaces: Palace[], tuHoa: TuHoa): Structure[] {
  const g = new Geo(palaces, tuHoa);
  return [cuMonHamHoaLoc(g), tamHoaHoiMenh(g), thanCuQuanLocVcd(g), coNguyetPhuThe(g), satPhaTham(g), ...kinhDuongTuMo(g)];
}

// ---------------------------------------------------------------- (c) named cách / groupings among fired rules

export interface LabelledFinding extends Labelled { claim: string; effect: Finding['effect']; basis: Finding['basis']; reading: string | null }

/** The fired rules that name a cách cục or a grouping (rule→concept link of kind 'formation' | 'classification'), exactly the `labelled`
 *  list kg/lift.ts returns, joined with the finding's claim/effect/basis and the rule's reading for display. Draft rules are left out unless
 *  asked for, as in lift(). */
export function labelledFindings(findings: Finding[], k: Knowledge, base: Record<string, Facts>, opts: { includeDraftRules?: boolean } = {}): LabelledFinding[] {
  // lift() walks the findings in order and keeps or drops a (rule, subject) pair as a whole (basis and link are per rule), so the n-th
  // labelled entry of a pair is that pair's n-th finding
  const byKey = new Map<string, Finding[]>();
  for (const f of findings) { const key = `${f.ruleId}\u0000${f.subject}`; byKey.set(key, [...(byKey.get(key) ?? []), f]); }
  const rules = new Map(k.rules.map(r => [r.id, r]));
  return lift(findings, k, base, opts).labelled.map(l => {
    const f = byKey.get(`${l.ruleId}\u0000${l.subject}`)!.shift()!;
    return { ...l, claim: f.claim, effect: f.effect, basis: f.basis, reading: rules.get(l.ruleId)?.reading ?? null };
  });
}
