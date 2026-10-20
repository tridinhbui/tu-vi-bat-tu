// The layers around the book readings of a palace (plan async-inventing-fairy, A1/A2). A palace chapter used to say only what fired
// book rules say, so a palace the books rarely discuss read as one line or nothing. Every chapter now reads:
//   1. structure (tinh_toan / sach tables): what the palace is about (KL pp.214-220), its chính tinh with the brightness the dignity tables
//      give (VERIFIED cells only), the star group (KL pp.166-167) or, vô chính diệu, the stars borrowed from the opposite palace; cát and
//      sát stars of the tam phương tứ chính; the natal Tứ Hóa on the palace (KL pp.195-197) and around it; Tuần / Triệt;
//   2. the book readings, unchanged (chapter.ts);
//   3. colour (pho_thong): what each chính tinh commonly means in this palace, bright or dim, and the notable phụ tinh. A star a voiced book
//      reading already speaks of is left to the book;
//   4. balance: every difficulty said above is answered — by the rescuing stars around the palace, or, failing those, by what the person
//      can do — and the advice of the cards voiced.
// pho_thong and tinh_toan sentences are labelled as such in the evidence panel; nothing here is said as the book's word.
import type { ChartInput, Knowledge, Palace } from '../types.ts';
import { Micro, finish, lowerFirst } from './micro.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';

export interface StructureLib {
  status: string; domain: string[]; majors: string[]; level: Record<string, string>;
  level_gist: Record<'bright' | 'dim' | 'mixed', string[]>; group: string[]; vcd: string[]; vcd_empty: string[];
  tp: Record<'cat' | 'sat' | 'mixed' | 'quiet', string[]>; hoa_self: string[]; hoa_tp: string[]; tuan: string[]; triet: string[];
  stars_kind: Record<'cat' | 'sat' | 'rescue', string[]>; domain_short: Record<string, string>; colour_lead: Record<'pair' | 'borrow' | 'pair_named' | 'borrow_named', string[]>; minor_lead: string[];
  balance: Record<'rescue' | 'self' | 'good' | 'advice', string[]>;
}
export interface MajorCard { core: string; bright: string; dim: string; advice: string }
export interface MinorCard { kind: 'cat' | 'sat' | 'trung'; line: string; advice: string; rescue: boolean }
export interface PhoThongLib { status: string; chinh: Record<string, Record<string, MajorCard>>; phu: Record<string, MinorCard>;
  /** what each Hóa brings to the palace it lands in (tu_hoa_cung.json) */
  hoa: Record<string, Record<string, string>> }

type Tone = 'neg' | 'answer' | 'pos';
export type DeepMove = 'STRUCT' | 'PHO_THONG' | 'BALANCE';
const BRIGHT = new Set(['miếu', 'vượng', 'đắc']);
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
/** phụ tinh worth a sentence of their own, in the order they are considered (at most three are voiced) */
const MINOR_ORDER = ['Địa Không', 'Địa Kiếp', 'Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Lộc Tồn', 'Tả Phụ', 'Hữu Bật', 'Văn Xương', 'Văn Khúc',
  'Thiên Khôi', 'Thiên Việt', 'Thiên Mã', 'Đào Hoa', 'Hồng Loan', 'Thiên Hỷ', 'Thiên Hình', 'Thiên Riêu', 'Thiên Khốc', 'Thiên Hư', 'Tang Môn', 'Bạch Hổ',
  'Cô Thần', 'Quả Tú', 'Hoa Cái', 'Thái Tuế', 'Thiên Y', 'Thiên Giải', 'Địa Giải', 'Giải Thần', 'Ân Quang', 'Thiên Quý', 'Thiên Quan', 'Thiên Phúc',
  'Long Trì', 'Phượng Các', 'Đại Hao', 'Tiểu Hao', 'Thiên Thương', 'Thiên Sứ', 'Lưu Hà', 'Kiếp Sát', 'Phá Toái'];

const join = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z0-9_]+)\}/g, (m, key) => v[key] ?? m);
/** card text and the person: {S} becomes the next anaphor, lower-case (it never opens a sentence in the cards) */
const withS = (t: string, m: Micro) => t.includes('{S}') ? t.replace(/\{S\}/g, () => lowerFirst(m.subject())) : t;

export interface PalaceRead { structure: ProseSentence[]; colour: ProseSentence[]; balance: ProseSentence[] }

/** The three layers for one palace. `bookStars`: stars a voiced book reading of this palace already speaks of (their card is not read);
 *  `key` keeps variant choice stable per use (a natal chapter and a đại hạn reading of the same palace pick independently). */
export function readPalace(chart: ChartInput, k: Knowledge, palName: string, m: Micro, o: { key: string; bookStars?: Set<string>; lead?: boolean }): PalaceRead {
  const S = k.prose?.structure as StructureLib | undefined, P = k.prose?.phoThong as PhoThongLib | undefined;
  const out: PalaceRead = { structure: [], colour: [], balance: [] };
  const REF = k.reference as Record<string, unknown> | undefined;
  if (!S || !P || !REF) return out;
  const pal = chart.palaces.find(p => p.name === palName) as Palace & { dignity_status?: Record<string, { status: string; value?: string; locator?: string }> };
  const base = chart.base[`palace:${palName}`] ?? {};
  const names = (base['palace.rel_names'] ?? {}) as Record<string, string>;
  const opp = chart.palaces.find(p => p.name === names.opp);
  const role = (REF.palaceRoles as { roles: Record<string, string> }).roles[palName] ?? palName;
  const domain = S.domain_short[palName] ?? role;
  const v = { pal: palName, role, domain, br: pal.branch };
  const key = (x: string) => `${o.key}|${palName}|${x}`;
  let step = '';                                            // which part of the reading a sentence is (trace.step): vanhan.ts picks parts
  const say = (bucket: ProseSentence[], text: string, move: DeepMove, basis: SentenceTrace['basis'], cites: string[] = [], tone?: Tone) => {
    const t = finish(withS(text, m)); m.said(t);
    bucket.push({ text: t, trace: { move, concepts: [], rules: [], cites: [...new Set(cites)].sort(), basis, step, ...(tone ? { tone } : {}) } });
  };
  const dig = (p: typeof pal, star: string) => { const d = p.dignity_status?.[star]; return d?.status === 'VERIFIED' ? { value: d.value!, cite: d.locator } : null; };
  const kind = (s: string) => S.stars_kind.cat.includes(s) ? 'cat' : S.stars_kind.sat.includes(s) ? 'sat' : null;
  const tpStars = (base['palace.rel.tp_stars'] ?? base['palace.tam_phuong_stars'] ?? []) as string[];
  const ownHoa = HOA.filter(h => (chart.tu_hoa[h] as { branch: number } | undefined)?.branch === pal.branch_index);
  const tpHoa = ((base['palace.tam_phuong_tu_hoa'] ?? []) as string[]).filter(h => !ownHoa.includes(h));
  let negatives = 0;

  // ---- 1. structure ----
  if (o.lead !== false) (step = 'domain', say)(out.structure, fill(m.pick(key('domain'), S.domain), v), 'STRUCT', 'tinh_toan', ['KL pp.214-220']);
  const majors = pal.major_stars;
  if (majors.length) {
    const ds = majors.map(s => dig(pal, s));
    const label = majors.map((s, i) => ds[i] ? `${s} (${S.level[ds[i]!.value] ?? ds[i]!.value})` : s);
    (step = 'majors', say)(out.structure, fill(m.pick(key('majors'), S.majors), { ...v, stars: join(label) }), 'STRUCT', 'tinh_toan', ds.flatMap(d => d?.cite ? [d.cite] : []));
    const known = ds.filter(Boolean) as Array<{ value: string }>;
    const bright = known.filter(d => BRIGHT.has(d.value)).length, dim = known.filter(d => d.value === 'hãm').length;
    if (bright && dim) (step = 'gist', say)(out.structure, m.pick(key('gist'), S.level_gist.mixed), 'STRUCT', 'pho_thong', [], 'neg');
    else if (dim) { (step = 'gist', say)(out.structure, m.pick(key('gist'), S.level_gist.dim), 'STRUCT', 'pho_thong', [], 'neg'); negatives++; }
    else if (bright) (step = 'gist', say)(out.structure, m.pick(key('gist'), S.level_gist.bright), 'STRUCT', 'pho_thong', [], 'pos');
    const gn = REF.groupNotes as { members: Record<string, string[]>; notes: Record<string, string> };
    const g = Object.entries(gn.members).find(([, ms]) => ms.includes(majors[0]));
    if (g) (step = 'group', say)(out.structure, fill(m.pick(key('group'), S.group), { star: majors[0], note: gn.notes[g[0]] }), 'STRUCT', 'tinh_toan', ['KL pp.166-167']);
  } else if (opp?.major_stars.length) {
    (step = 'vcd', say)(out.structure, fill(m.pick(key('vcd'), S.vcd), { ...v, opp: opp.name, opp_majors: join(opp.major_stars) }), 'STRUCT', 'pho_thong');
  } else (step = 'vcd', say)(out.structure, fill(m.pick(key('vcd'), S.vcd_empty), v), 'STRUCT', 'pho_thong');
  const cats = [...new Set(tpStars.filter(s => kind(s) === 'cat'))], sats = [...new Set(tpStars.filter(s => kind(s) === 'sat'))];
  const tpKind = cats.length >= 2 && sats.length >= 2 ? 'mixed' : cats.length >= 2 ? 'cat' : sats.length >= 2 ? 'sat' : cats.length && sats.length ? 'mixed' : 'quiet';
  (step = 'tp', say)(out.structure, fill(m.pick(key('tp'), S.tp[tpKind]), { ...v, cats: join(cats), sats: join(sats) }), 'STRUCT', 'pho_thong', [],
    tpKind === 'sat' ? 'neg' : tpKind === 'cat' ? 'pos' : undefined);
  if (tpKind === 'sat' || (tpKind === 'mixed' && sats.length > cats.length)) negatives++;
  const th = REF.tuHoa as { meaning: Record<string, string>; positionNotes: Record<string, string> };
  for (const h of ownHoa) {
    const star = (chart.tu_hoa[h] as { star: string }).star;
    // the book's position note is generic only for Hóa Kỵ; the others' notes are examples from other palaces
    const note = h === 'Hóa Kỵ' && th.positionNotes[h] ? `; ${th.positionNotes[h]}` : '';
    (step = 'hoa', say)(out.structure, fill(m.pick(key(`hoa|${h}`), S.hoa_self), { ...v, hoa: `${h} (${star})`, meaning: th.meaning[h], note }), 'STRUCT', 'tinh_toan', ['KL pp.195-197'], h === 'Hóa Kỵ' ? 'neg' : 'pos');
    if (h === 'Hóa Kỵ') negatives++;
  }
  if (tpHoa.length) (step = 'hoa_tp', say)(out.structure, fill(m.pick(key('hoa_tp'), S.hoa_tp), { ...v, hoas: join(tpHoa) }), 'STRUCT', 'pho_thong');
  if (pal.tuan) (step = 'tuan', say)(out.structure, fill(m.pick(key('tuan'), S.tuan), v), 'STRUCT', 'pho_thong');
  if (pal.triet) (step = 'triet', say)(out.structure, fill(m.pick(key('triet'), S.triet), v), 'STRUCT', 'pho_thong');

  // ---- 3. colour (pho_thong cards) ----
  const advice: string[] = [];
  const book = o.bookStars ?? new Set<string>();
  const readMajor = (star: string, p: Palace, borrowed: boolean, second: boolean) => {
    const c = P.chinh[star]?.[palName];
    if (!c) return;
    const d = borrowed ? null : dig(p as typeof pal, star);
    const isDim = d?.value === 'hãm';
    advice.push(c.advice);
    if (book.has(star)) return;
    // a card that opens with the star's own name keeps its capital, under a lead that does not name the star again
    const named = c.core.startsWith(star), text = named ? c.core : lowerFirst(c.core);
    const lead = (k: 'borrow' | 'pair') => named ? S.colour_lead[`${k}_named`] : S.colour_lead[k];
    const core = borrowed ? fill(m.pick(key(`borrow|${star}`), lead('borrow')), { star, text })
      : second ? fill(m.pick(key(`pair|${star}`), lead('pair')), { star, text }) : c.core;
    step = 'colour'; say(out.colour, core, 'PHO_THONG', 'pho_thong');
    if (d && BRIGHT.has(d.value)) say(out.colour, c.bright, 'PHO_THONG', 'pho_thong', [], 'pos');
    else if (isDim) say(out.colour, c.dim, 'PHO_THONG', 'pho_thong', [], 'neg');
  };
  if (majors.length) majors.forEach((s, i) => readMajor(s, pal, false, i > 0));
  else if (opp) opp.major_stars.slice(0, 1).forEach(s => readMajor(s, opp, true, false));
  // at most three phụ tinh, harsh and helpful in turn so the colour does not lean one way: the first of each kind, then the next
  const cand = MINOR_ORDER.filter(s => pal.stars.includes(s) && P.phu[s]);
  const hard = cand.filter(s => P.phu[s].kind === 'sat'), soft = cand.filter(s => P.phu[s].kind !== 'sat');
  const minors = [hard[0], soft[0], hard[1] ?? soft[1], soft[1] ?? hard[1]].filter((s, i, a): s is string => !!s && a.indexOf(s) === i).slice(0, 3);
  for (const s of minors) {
    const c = P.phu[s];
    step = 'minor'; say(out.colour, fill(c.line, v), 'PHO_THONG', 'pho_thong', [], c.kind === 'sat' ? 'neg' : c.kind === 'cat' ? 'pos' : undefined);
    if (c.kind === 'sat') { negatives++; advice.unshift(fill(c.advice, v)); }
  }
  if (ownHoa.includes('Hóa Kỵ') && P.phu['Hóa Kỵ']) advice.unshift(fill(P.phu['Hóa Kỵ'].advice, v));

  // ---- 4. balance: what answers the difficulties, then what to do ----
  const rescuers = [...new Set([...tpStars.filter(s => S.stars_kind.rescue.includes(s)), ...[...ownHoa, ...tpHoa].filter(h => h !== 'Hóa Kỵ')])];
  if (negatives) {
    if (rescuers.length) (step = 'rescue', say)(out.balance, fill(m.pick(key('rescue'), S.balance.rescue), { ...v, rescuers: join(rescuers.slice(0, 4)) }), 'BALANCE', 'pho_thong', [], 'answer');
    else (step = 'self', say)(out.balance, fill(m.pick(key('self'), S.balance.self), v), 'BALANCE', 'pho_thong', [], 'answer');
  } else if (tpKind === 'cat' || out.structure.some(s => (s.trace as { tone?: Tone }).tone === 'pos')) (step = 'good', say)(out.balance, fill(m.pick(key('good'), S.balance.good), v), 'BALANCE', 'pho_thong', [], 'answer');
  const adv = [...new Set(advice.map(a => fill(a, v).replace(/\.$/, '')))].slice(0, 2);
  if (adv.length) (step = 'advice', say)(out.balance, fill(m.pick(key('advice'), S.balance.advice), { ...v, advice: adv.join(', đồng thời ') }), 'BALANCE', 'pho_thong', [], 'answer');
  return out;
}

/** stars named in the conditions of the book rules a chapter voices: the cards of these stars are not read in that chapter */
export function bookStarsOf(paragraphs: ProseParagraph[], k: Knowledge, palace: Palace, opp?: Palace): Set<string> {
  const ids = new Set(paragraphs.flatMap(p => p.sentences.flatMap(s => s.trace.rules)));
  const conds = k.rules.filter(r => ids.has(r.id)).map(r => JSON.stringify(r.conditions));
  return new Set([...palace.major_stars, ...(opp?.major_stars ?? [])].filter(s => conds.some(c => c.includes(`"${s}"`))));
}

export const para = (role: ProseParagraph['role'], sentences: ProseSentence[]): ProseParagraph[] =>
  sentences.length ? [{ role, sentences, text: sentences.map(s => s.text).join(' ') }] : [];
