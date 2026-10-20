// Bát Tự structure prose (plan async-inventing-fairy, C): what the structure analysis (engine/tvbt/bazi_deep, facts.bazi.deep) computes,
// told chapter by chapter. Basis per sentence:
//   - sach: a verified rule that fired (BT_TVH_* on strength, the TTT 歲運 rules on luck pillars), with its id;
//   - tinh_toan: a computed fact or a page-cited table (TVH score pp.331-355, the TVH điều hậu table pp.389-396, the month's season state);
//   - pho_thong: the phù ức reading (a system principle), the cách names (draft definitions) and the cards of content/prose/pho_thong/bat_tu.json.
// Balanced on purpose: a luck pillar that meets an element to avoid is told with what to do, never as a verdict.
import type { ChartInput, Knowledge } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';

export interface BaziDeep {
  strength: { dm_strong: boolean | null; own_share: number | null; threshold: number | null; season_state: string | null };
  climate: { label: string | null; han_noan: string | null };
  dieu_hau: { cell: string | null; need: string[]; avoid: string[]; satisfied: boolean | null; verified: boolean;
    stems: Array<{ stem: string; ten_god: string; rank: string; visible: boolean; hidden: boolean }> };
  phu_uc: Array<{ level: string; yong: string[]; xi: string[]; ji: string[] }>;
  geju: { inner: Array<{ name: string; state: string | null }>; outer: Array<{ name: string; quality: string | null }> };
  verified: Array<{ rule_id: string; claim: string; text: string }>;
  luck: Array<{ index: number; pillar: string; ten_god: string | null; level: string | null; effect: string | null; can_chi: string[];
    dieu_hau: { stem: string | null; branch: string | null }; findings: Array<{ rule_id: string; text: string }> }>;
}
export interface BaziDeepFrames {
  season: string[]; season_state: Record<string, string>; strength_border: string[]; strength_side: string[]; climate: string[]; climate_presence: string[];
  need: string[]; phu_uc: string[]; geju_inner: string[]; geju_outer: string[]; geju_state: Record<string, string>; luck: string[];
  luck_role: Record<string, string>; luck_branch_role: Record<string, string>; luck_pu: Record<'yong' | 'xi' | 'ji', string[]>; verified_text: Record<string, string>; pillar_lead: Record<string, string>;
}
export interface BaziCards {
  ten_god_pillar: Record<string, Record<string, string>>; ten_god_luck: Record<string, { line: string; good: string; hard: string; advice: string }>;
  element: Record<string, { strong: string; weak: string; missing: string; practical: string }>; strength: Record<string, { line: string; advice: string }>;
  dung_than: Record<string, string>;
}
type Ch = 'nhat-chu' | 'ngu-hanh' | 'su-nghiep' | 'quan-he' | 'dai-van' | 'cach-cuc';

const GROUP: Record<string, string> = { 'Tỉ Kiên': 'Tỉ Kiếp', 'Kiếp Tài': 'Tỉ Kiếp', 'Thực Thần': 'Thực Thương', 'Thương Quan': 'Thực Thương', 'Chính Tài': 'Tài', 'Thiên Tài': 'Tài',
  'Chính Quan': 'Quan Sát', 'Thất Sát': 'Quan Sát', 'Chính Ấn': 'Ấn', 'Thiên Ấn': 'Ấn' };
const join = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, k) => v[k] ?? m);
const STEM_EL: Record<string, string> = { 'Giáp': 'Mộc', 'Ất': 'Mộc', 'Bính': 'Hỏa', 'Đinh': 'Hỏa', 'Mậu': 'Thổ', 'Kỷ': 'Thổ', 'Canh': 'Kim', 'Tân': 'Kim', 'Nhâm': 'Thủy', 'Quý': 'Thủy' };
const BRANCH_EL: Record<string, string> = { 'Tý': 'Thủy', 'Sửu': 'Thổ', 'Dần': 'Mộc', 'Mão': 'Mộc', 'Thìn': 'Thổ', 'Tỵ': 'Hỏa', 'Ngọ': 'Hỏa', 'Mùi': 'Thổ', 'Thân': 'Kim', 'Dậu': 'Kim', 'Tuất': 'Thổ', 'Hợi': 'Thủy' };

export function deepBazi(chart: ChartInput, k: Knowledge, m: Micro, F: BaziDeepFrames | undefined, C: BaziCards | undefined,
  rules: Record<string, { reading: string; cites: string[]; verified: boolean }>): Partial<Record<Ch, ProseParagraph[]>> {
  const b = chart.bazi as (ChartInput['bazi'] & { deep?: BaziDeep | null }) | undefined, D = b?.deep;
  if (!b || !D || !F) return {};
  const S = () => lowerFirst(m.subject());
  const say = (xs: ProseSentence[], text: string, basis: SentenceTrace['basis'], cites: string[] = [], ids: string[] = [], tone?: 'pos' | 'neg' | 'answer') => {
    const t = finish(text.replace(/\{S\}/g, () => S())); m.said(t);
    xs.push({ text: t, trace: { move: 'ELABORATE', concepts: [], rules: ids, cites, basis, ...(tone ? { tone } : {}) } });
  };
  const fired = new Map(D.verified.map(v => [v.rule_id, v]));
  const cite = (id: string, text: string, cites: string[]) => { rules[id] = { reading: text, cites, verified: true }; return id; };
  const pil = b.pillars, dm = b.day_master, el = b.day_master_element, mb = pil.month.branch;
  const out: Partial<Record<Ch, ProseParagraph[]>> = {};
  const para = (id: Ch, xs: ProseSentence[]) => { if (xs.length) (out[id] ??= []).push({ role: 'support', sentences: xs, text: xs.map(s => s.text).join(' ') }); };

  // ---- nhật chủ: season, strength by TVH's score, what the level means ----
  const st: ProseSentence[] = [];
  if (D.strength.season_state) say(st, fill(m.pick('bd|season', F.season), { dm, el, mb, state: F.season_state[D.strength.season_state] ?? D.strength.season_state }), 'tinh_toan', ['ZZ (ngũ hành vượng tướng hưu tù tử)']);
  const sh = D.strength.own_share, th = D.strength.threshold;
  const border = fired.has('BT_TVH_BIEN');
  let levelKey = 'trung hòa';
  if (sh != null && th != null) {
    const pct = String(Math.round(sh * 100)), thp = String(Math.round(th * 100));
    if (border) say(st, fill(m.pick('bd|border', F.strength_border), { pct, th: thp }), 'sach', ['TVH pp.331-355'], [cite('BT_TVH_BIEN', fired.get('BT_TVH_BIEN')!.text, ['TVH pp.331-355'])]);
    else {
      const strong = !!D.strength.dm_strong;
      levelKey = strong ? 'vượng' : 'nhược';
      const id = strong ? 'BT_TVH_VUONG' : 'BT_TVH_NHUOC', v = fired.get(id);
      say(st, fill(m.pick('bd|side', F.strength_side), { pct, th: thp, cmp: strong ? 'vượt' : 'dưới', side: strong ? 'thuộc thế vượng' : 'thuộc thế nhược' }),
        v ? 'sach' : 'tinh_toan', ['TVH pp.331-355'], v ? [cite(id, v.text, ['TVH pp.331-355'])] : []);
    }
  }
  const sc = C?.strength[levelKey];
  if (sc) { say(st, sc.line, 'pho_thong'); say(st, `Điều nên giữ: ${sc.advice}.`, 'pho_thong', [], [], 'answer'); }
  para('nhat-chu', st);

  // ---- cách cục và dụng thần: the cách, điều hậu (verified table), phù ức, what the useful element means ----
  const cc: ProseSentence[] = [];
  for (const g of D.geju.inner.slice(0, 1)) say(cc, fill(m.pick('bd|gi', F.geju_inner), { name: g.name, state: F.geju_state[g.state ?? ''] ?? g.state ?? '' }), 'pho_thong');
  for (const g of D.geju.outer.slice(0, 1)) if (g.quality === 'giả') say(cc, fill(m.pick('bd|go', F.geju_outer), { name: g.name, quality: 'giả cách' }), 'pho_thong');
  const dh = D.dieu_hau;
  if (dh.verified && dh.stems.length) {
    const main = dh.stems.filter(s => s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`), others = dh.stems.filter(s => !s.rank.startsWith('chính')).map(s => `${s.stem} (${s.ten_god})`);
    say(cc, fill(m.pick('bd|cl', F.climate), { mb, dm, climate: D.climate.label ?? '', main: join(main.length ? main : others.slice(0, 1)), others: join(main.length ? others : others.slice(1)) || 'không có can nào khác' }),
      'tinh_toan', ['TVH pp.389-396']);
    const present = dh.stems.filter(s => s.visible || s.hidden).map(s => s.stem), absent = dh.stems.filter(s => !s.visible && !s.hidden).map(s => s.stem);
    if (present.length && absent.length) say(cc, fill(m.pick('bd|pr', F.climate_presence), { present: join(present), absent: join(absent) }), 'tinh_toan', ['TVH pp.389-396']);
    for (const [id, v] of fired) if (F.verified_text[id] && id.startsWith('BT_TTT_HANNOAN')) say(cc, F.verified_text[id], 'sach', ['TTT'], [cite(id, v.text, ['TTT'])]);
    if (dh.need.length) say(cc, fill(m.pick('bd|need', F.need), { need: join(dh.need), avoid: join(dh.avoid) || 'không có hành nào cần tránh rõ' }), 'tinh_toan', ['TVH pp.389-396']);
  }
  const pu = D.phu_uc[0];
  if (pu?.yong.length) say(cc, fill(m.pick('bd|pu', F.phu_uc), { level: border ? 'nghiêng về nhược' : pu.level, yong: join(pu.yong), xi: join(pu.xi) || 'không nhóm nào', ji: join(pu.ji) }), 'pho_thong');
  for (const e of dh.need) if (C?.dung_than[e]) say(cc, C.dung_than[e], 'pho_thong', [], [], 'answer');
  for (const e of dh.need) if (C?.element[e]) say(cc, C.element[e].practical, 'pho_thong', [], [], 'answer');
  para('cach-cuc', cc);

  // ---- ngũ hành: the strongest, weakest and missing elements among the eight characters ----
  const K = ['year', 'month', 'day', 'hour'] as const;
  const els = K.flatMap(x => [STEM_EL[pil[x].stem], BRANCH_EL[pil[x].branch]]);
  const count = ['Mộc', 'Hỏa', 'Thổ', 'Kim', 'Thủy'].map(e => [e, els.filter(x => x === e).length] as const);
  const nh: ProseSentence[] = [];
  const max = Math.max(...count.map(([, n]) => n));
  if (C) {
    for (const [e, n] of count) if (n === max && n >= 3 && C.element[e]) say(nh, C.element[e].strong, 'pho_thong', [], [], 'neg');
    for (const [e, n] of count) if (n === 0 && C.element[e]) say(nh, C.element[e].missing, 'pho_thong', [], [], 'neg');
    for (const [e, n] of count) if (n === 1 && C.element[e]) say(nh, C.element[e].weak, 'pho_thong');
  }
  para('ngu-hanh', nh);

  // ---- sự nghiệp, quan hệ: what the ten gods mean where they stand ----
  const bf = b.base.chart as Record<string, unknown>;
  const at: Array<[string, string | null | undefined, Ch]> = [['month', pil.month.stem_ten_god, 'su-nghiep'], ['hour', pil.hour.stem_ten_god, 'su-nghiep'],
    ['year', pil.year.stem_ten_god, 'quan-he'], ['day_branch', bf['bazi.day_main_god'] as string | undefined, 'quan-he']];
  const byCh: Partial<Record<Ch, ProseSentence[]>> = {};
  for (const [pos, god, ch] of at) {
    const t = god && C?.ten_god_pillar[god]?.[pos];
    // the card opens "<god> ở trụ tháng …": the lead already names both, so the card's own opening is dropped
    const body = t ? t.replace(new RegExp(`^${god}\\s*(ở\\s+(trụ\\s+\\S+|chi\\s+ngày)\\s*)?`), '') : '';
    if (t) say(byCh[ch] ??= [], fill(F.pillar_lead[pos], { god: god!, text: lowerFirst(body || t) }), 'pho_thong');
  }
  for (const [ch, xs] of Object.entries(byCh)) para(ch as Ch, xs);

  // ---- đại vận: one paragraph per luck pillar, from the first that starts after birth ----
  const yr = chart.year?.year ?? new Date().getFullYear();
  for (const l of D.luck) {
    const meta = b.luck[l.index - 1] ?? b.luck.find(x => x.name === l.pillar);
    if (!meta || meta.start_year == null || meta.start_age > 80) continue;
    const xs: ProseSentence[] = [];
    say(xs, fill(m.pick(`bd|lk${l.index}`, F.luck), { age: String(Math.round(meta.start_age)), year: String(meta.start_year), pillar: l.pillar, god: l.ten_god ?? '—' }), 'tinh_toan', ['ZZ (đại vận)']);
    const card = l.ten_god ? C?.ten_god_luck[l.ten_god] : undefined;
    if (card) say(xs, card.line, 'pho_thong');
    // the stem's role: by the điều hậu table when the stem is one of its stems, otherwise by the phù ức reading (system principle)
    const g = l.ten_god ? GROUP[l.ten_god] : undefined, pu = D.phu_uc[0];
    const puRole = g && pu ? (pu.yong.includes(g) ? 'yong' : pu.xi.includes(g) ? 'xi' : pu.ji.includes(g) ? 'ji' : null) : null;
    const role = l.dieu_hau.stem ?? puRole ?? 'none';
    if (l.dieu_hau.stem && F.luck_role[role]) say(xs, F.luck_role[role], 'tinh_toan', ['TVH pp.389-396'], [], role === 'ji' ? 'neg' : 'pos');
    else if (puRole && F.luck_pu) say(xs, fill(m.pick(`bd|pu${l.index}`, F.luck_pu[puRole]), { god: l.ten_god!, group: g! }), 'pho_thong', [], [], puRole === 'ji' ? 'neg' : 'pos');
    else if (F.luck_role.none) say(xs, F.luck_role.none, 'tinh_toan', ['TVH pp.389-396']);
    if (l.dieu_hau.branch && F.luck_branch_role[l.dieu_hau.branch]) say(xs, F.luck_branch_role[l.dieu_hau.branch], 'tinh_toan', ['TVH pp.389-396'], [], l.dieu_hau.branch === 'ji' ? 'neg' : 'pos');
    for (const f of l.findings) if (F.verified_text[f.rule_id]) say(xs, F.verified_text[f.rule_id], 'sach', ['TTT'], [cite(f.rule_id, f.text, ['TTT'])], 'neg');
    if (card) {
      // the card's two readings open "Khi là kỵ thần / dụng thần, …": the role was said just above, so the opening goes
      const plain = (t: string) => t.replace(/^Khi (là|làm) (kỵ|dụng|hỷ) thần,\s*/, '');
      if (role === 'ji') say(xs, plain(card.hard), 'pho_thong', [], [], 'neg');
      else if (role === 'yong' || role === 'xi') say(xs, plain(card.good), 'pho_thong', [], [], 'pos');
      say(xs, `Trong vận này, nên ${card.advice}.`, 'pho_thong', [], [], 'answer');
    }
    if (meta.start_year <= yr + 60) para('dai-van', xs);
  }
  return out;
}
