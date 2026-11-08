// The Bát Tự side of G9 (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G9.1): the chart as a graph, read from the facts the engine already
// computes (facts.bazi: pillars with hidden stems and ten gods, natal relations, deep.cach_tvh / deep.depth.yong / deep.dieu_hau).
//   nodes   each stem and each hidden stem, with its element, ten-god group and its role in the element map (G2.3): dụng / hỷ / kỵ / xấu
//           (the cách table's bad groups) / nhàn, and whether the điều hậu cell names it
//   edges   sinh / khắc between neighbouring stems (đứng sát), the hidden stems of a branch under its stem (cùng trụ), roots of the day master
//           (thông căn), and the natal hợp / xung / hình of facts.bazi.relations
//   chains  Tài → Quan → Ấn → nhật chủ graded mạnh / vừa / yếu / đứt (G3.1, a labelled convention)
// Data only: the prose reads parts of it (bazi_deep.ts element map, bazi_kin.ts chain grade); /api/interpret returns it with analysis: true.
import type { ChartInput } from '../types.ts';

export const BAZI_GRAPH_VERSION = 'bazi-graph-0.1.0';
type PK = 'year' | 'month' | 'day' | 'hour';
const PKS: PK[] = ['year', 'month', 'day', 'hour'];
const STEM_EL: Record<string, string> = { Giáp: 'Mộc', Ất: 'Mộc', Bính: 'Hỏa', Đinh: 'Hỏa', Mậu: 'Thổ', Kỷ: 'Thổ', Canh: 'Kim', Tân: 'Kim', Nhâm: 'Thủy', Quý: 'Thủy' };
const GEN: Record<string, string> = { Mộc: 'Hỏa', Hỏa: 'Thổ', Thổ: 'Kim', Kim: 'Thủy', Thủy: 'Mộc' };
const CTRL: Record<string, string> = { Mộc: 'Thổ', Thổ: 'Thủy', Thủy: 'Hỏa', Hỏa: 'Kim', Kim: 'Mộc' };
const GROUP: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
export type ElRole = 'dung' | 'hy' | 'ky' | 'xau' | 'nhan';
export interface BNode { id: string; pillar: PK; kind: 'stem' | 'hidden'; stem: string; element: string; god: string | null; group: string | null; role: ElRole; dieuHau?: 'chinh' | 'phu' }
export interface BEdge { kind: 'sinh' | 'khac' | 'cung_tru' | 'thong_can' | 'hop' | 'xung' | 'hinh' | 'hai'; from: string; to: string }
export interface Chain { from: 'Tài' | 'Quan Sát'; grade: 'manh' | 'vua' | 'yeu' | 'dut'; path: string[]; why: string }
export interface ElementRow { element: string; group: string; role: ElRole; dieuHau: Array<{ stem: string; rank: 'chinh' | 'phu' }>; agree: 'cung_chieu' | 'venh' | 'mot_phia' | null }
export interface BaziGraph { version: string; nodes: BNode[]; edges: BEdge[]; chains: Chain[]; elements: ElementRow[]; basis: 'he_thong' }

type Pillar = { stem: string; branch: string; stem_ten_god: string | null; hidden: Array<{ stem: string; ten_god: string }> };
type Deep = { cach_tvh?: { yong: string[]; van_xau: string[] }; depth?: { yong?: { group: string; hy?: { group: string }; ky?: { group: string } } };
  dieu_hau?: { verified: boolean; stems: Array<{ stem: string; ten_god: string; rank: string }> } };

export function baziGraph(chart: ChartInput): BaziGraph | null {
  const b = chart.bazi as { pillars?: Record<PK, Pillar>; relations?: Record<string, Array<{ pillars: string }>>; deep?: Deep } | undefined;
  if (!b?.pillars) return null;
  const pil = b.pillars, dmEl = STEM_EL[pil.day.stem], D = b.deep ?? {};
  const Y = D.depth?.yong, yong = new Set([...(D.cach_tvh?.yong ?? []), ...(Y?.group ? [Y.group] : [])]), xau = new Set(D.cach_tvh?.van_xau ?? []);
  const groupOfEl = (el: string) => el === dmEl ? 'Tỉ Kiếp' : GEN[el] === dmEl ? 'Ấn' : GEN[dmEl] === el ? 'Thực Thương' : CTRL[dmEl] === el ? 'Tài' : 'Quan Sát';
  const roleOf = (g: string | null): ElRole => !g ? 'nhan' : yong.has(g) ? 'dung' : g === Y?.hy?.group ? 'hy' : g === Y?.ky?.group ? 'ky' : xau.has(g) ? 'xau' : 'nhan';
  const dh = D.dieu_hau?.verified ? D.dieu_hau.stems : [];
  const dhOf = (stem: string) => { const x = dh.find(s => s.stem === stem); return x ? (x.rank.startsWith('chính') ? 'chinh' as const : 'phu' as const) : undefined; };
  const nodes: BNode[] = [], edges: BEdge[] = [];
  for (const p of PKS) {
    const P = pil[p], sid = `${p}.stem`;
    const sg = p === 'day' ? 'Tỉ Kiếp' : GROUP[P.stem_ten_god ?? ''] ?? null;
    nodes.push({ id: sid, pillar: p, kind: 'stem', stem: P.stem, element: STEM_EL[P.stem], god: p === 'day' ? 'nhật chủ' : P.stem_ten_god, group: sg, role: p === 'day' ? 'nhan' : roleOf(sg), ...(dhOf(P.stem) ? { dieuHau: dhOf(P.stem) } : {}) });
    P.hidden.forEach((h, i) => {
      const id = `${p}.hidden.${i}`, g = GROUP[h.ten_god] ?? null;
      nodes.push({ id, pillar: p, kind: 'hidden', stem: h.stem, element: STEM_EL[h.stem], god: h.ten_god, group: g, role: roleOf(g), ...(dhOf(h.stem) ? { dieuHau: dhOf(h.stem) } : {}) });
      edges.push({ kind: 'cung_tru', from: sid, to: id });
      if (STEM_EL[h.stem] === dmEl) edges.push({ kind: 'thong_can', from: id, to: 'day.stem' });
    });
  }
  // sinh / khắc between neighbouring stems (year–month, month–day, day–hour) and between a stem and the hidden stems under it
  const near: Array<[string, string]> = [['year.stem', 'month.stem'], ['month.stem', 'day.stem'], ['day.stem', 'hour.stem']];
  for (const n of nodes.filter(x => x.kind === 'hidden')) near.push([`${n.pillar}.stem`, n.id]);
  const nd = (id: string) => nodes.find(x => x.id === id)!;
  for (const [a, c] of near) for (const [x, y] of [[a, c], [c, a]]) {
    if (GEN[nd(x).element] === nd(y).element) edges.push({ kind: 'sinh', from: x, to: y });
    if (CTRL[nd(x).element] === nd(y).element) edges.push({ kind: 'khac', from: x, to: y });
  }
  const REL: Record<string, BEdge['kind']> = { stem_combine: 'hop', branch_six_combine: 'hop', stem_clash: 'xung', branch_clash: 'xung', branch_penalty: 'hinh', branch_harm: 'hai' };
  for (const [k, kind] of Object.entries(REL)) for (const r of b.relations?.[k] ?? []) { const [a, c] = r.pillars.split('-'); edges.push({ kind, from: `${a}.${k.startsWith('stem') ? 'stem' : 'branch'}`, to: `${c}.${k.startsWith('stem') ? 'stem' : 'branch'}` }); }
  // chains to the day master (G3.1): Ấn on a stem next to the day master with Quan next to it: mạnh; Ấn hidden right under a Quan stem next to
  // the day master: vừa; Ấn only hidden farther, or Quan only hidden: yếu; no Ấn or no Quan: đứt
  const chains: Chain[] = [];
  const at = (g: string, kind?: 'stem' | 'hidden') => nodes.filter(n => n.group === g && n.god !== 'nhật chủ' && (!kind || n.kind === kind));
  const nextTo = (n: BNode) => n.kind === 'stem' ? n.pillar === 'month' || n.pillar === 'hour' : n.pillar === 'day';
  const an = at('Ấn'), quan = at('Quan Sát');
  const anNear = an.filter(n => n.kind === 'stem' && nextTo(n)), quanNearStem = quan.filter(n => n.kind === 'stem' && nextTo(n));
  const under = an.find(n => n.kind === 'hidden' && quanNearStem.some(q => q.pillar === n.pillar));
  let grade: Chain['grade'], path: string[], why: string;
  if (!an.length || !quan.length) { grade = 'dut'; path = []; why = !an.length ? 'không có Ấn' : 'không có Quan Sát'; }
  else if (anNear.length && quan.some(q => q.kind === 'stem')) { grade = 'manh'; path = [quan.find(q => q.kind === 'stem')!.id, anNear[0].id, 'day.stem']; why = 'Ấn lộ ở can đứng sát nhật chủ, Quan lộ trên can'; }
  else if (under) { const q = quanNearStem.find(x => x.pillar === under.pillar)!; grade = 'vua'; path = [q.id, under.id, 'day.stem']; why = `${under.stem} (${under.god}) tàng ngay dưới ${q.stem} (${q.god}), trụ đứng sát nhật chủ`; }
  else { grade = 'yeu'; path = [quan[0].id, an[0].id, 'day.stem']; why = 'Ấn chỉ tàng ở trụ xa, hoặc Quan chỉ tàng'; }
  chains.push({ from: 'Quan Sát', grade, path, why });
  const tai = at('Tài');
  const taiQ = tai.some(t => t.kind === 'stem') && quan.some(q => q.kind === 'stem') ? 'vua' : tai.length && quan.length ? 'yeu' : 'dut';
  chains.push({ from: 'Tài', grade: taiQ, path: taiQ === 'dut' ? [] : [tai[0].id, quan[0].id], why: taiQ === 'vua' ? 'Tài và Quan cùng lộ trên can' : taiQ === 'yeu' ? 'Tài hoặc Quan chỉ tàng' : 'thiếu Tài hoặc Quan' });
  // the element map: each element with its group, its role, the điều hậu stems of it, and whether the two readings agree there
  const elements: ElementRow[] = ['Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy'].map(el => {
    const g = groupOfEl(el), role = roleOf(g), dhs = dh.filter(s => STEM_EL[s.stem] === el).map(s => ({ stem: s.stem, rank: s.rank.startsWith('chính') ? 'chinh' as const : 'phu' as const }));
    return { element: el, group: g, role, dieuHau: dhs, agree: !dhs.length ? null : role === 'dung' || role === 'hy' ? 'cung_chieu' : role === 'ky' || role === 'xau' ? 'venh' : 'mot_phia' };
  });
  return { version: BAZI_GRAPH_VERSION, nodes, edges, chains, elements, basis: 'he_thong' };
}
