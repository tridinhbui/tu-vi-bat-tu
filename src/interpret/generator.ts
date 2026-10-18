// Deterministic narrative generator: argument graph + editorial modules -> Vietnamese chapter.
// Slots are filled only from the argument graph (chart facts, fired verified rules and their pages); a passage whose slot is empty or
// unknown is skipped, never padded. Variant choice is a hash of (chart, module, passage) that skips variants whose opening words were
// used in the last sentences, so the same chart always reads the same and different charts do not read like one template.
import { joinVi } from './semantic.ts';
import type { ArgumentGraph, Claim } from './planner.ts';
import type { Basis, ContentModule, Knowledge, ModuleCond, Passage } from './types.ts';

export interface Sentence { text: string; basis: Basis; kind: string; module: string; passage: string; rules: string[]; cites: string[] }
export interface Paragraph { module: string; role: string; title: string; sentences: Sentence[]; text: string }
type Slot = { text: string; rules: string[] };

const BOOK: Record<string, string> = { TH: 'Thực Hành', KL: 'Khảo Luận', TT: 'Toàn Thư' };
export const citeVi = (c: string) => { const m = c.match(/^(TH|KL|TT)\s+(?:pp?\.)?\s*(.+)$/); return m ? `${BOOK[m[1]]} tr.${m[2].replace(/-/g, '–')}` : c; };
const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : s;

function hash(s: string): number { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const opener = (t: string) => t.replace(/[^\p{L}\p{N} ]/gu, ' ').trim().split(/\s+/).slice(0, 2).join(' ').toLowerCase();

function citesOf(c: Claim): string[] { return [...new Set(c.grounds.flatMap(g => g.cites))].map(citeVi); }
function quoteList(c: Claim): string { return joinVi(c.quotes.map(q => `“${q}”`)); }
function claimItem(c: Claim, withCond: boolean): string {
  if (!withCond) { const cites = citesOf(c); return `${quoteList(c)}${cites.length ? ` (${cites.join('; ')})` : ''}`; }
  return c.grounds.map(g => {
    const qs = joinVi([...new Set(g.evidence.map(e => `“${e.core}”`))]), cites = [...new Set(g.cites)].map(citeVi);
    const cond = g.evidence[0].chartCondition;
    return `${qs}${cond ? ` khi ${cond}` : ''}${cites.length ? ` (${cites.join('; ')})` : ''}`;
  }).join('; ');
}

export class Realizer {
  slots = new Map<string, Slot>(); lists = new Map<string, Claim[]>(); items = new Map<string, Array<Record<string, Slot>>>();
  a: ArgumentGraph; k: Knowledge; seed: string; capScale: number;
  constructor(a: ArgumentGraph, k: Knowledge, seed: string, capScale = 1) { this.a = a; this.k = k; this.seed = seed; this.capScale = capScale; this.prepare(); }

  private set(key: string, text: string, rules: string[] = []) { this.slots.set(key, { text, rules }); }

  private prepare() {
    const a = this.a;
    for (const [k, v] of Object.entries(a.slots)) this.set(k, v);
    const L = (name: string, cs: Claim[]) => this.lists.set(name, cs);
    L('base', a.lists.base); L('support', a.lists.support); L('cross', a.lists.cross); L('work_style', a.lists.work_style);
    L('qualifier_quan', a.lists.qualifier.filter(c => c.palace === a.career));
    L('qualifier_other', a.lists.qualifier.filter(c => c.palace !== a.career));
    L('environment', a.lists.environment);
    L('env_pos', a.lists.environment.filter(c => c.polarity !== '-')); L('env_neg', a.lists.environment.filter(c => c.polarity === '-'));
    L('timing', a.lists.timing);
    L('dominance', a.dominance.map(d => d.qualifier));
    this.set('than.is_opp', a.slots['than.palace'] === a.opposite ? '1' : '');

    // claims whose several book sentences stand on ONE ground (the dedup the reader should see)
    this.items.set('shared_ground', a.claims.filter(c => c.role === 'base' || c.role === 'support').flatMap(c => c.grounds.filter(g => g.evidence.length >= 2).map(g => ({
      's.quotes': { text: cap(joinVi(g.evidence.map(e => `“${e.core}”`))), rules: g.evidence.map(e => e.rule.id) },
      's.n': { text: ['', 'một', 'hai', 'ba', 'bốn', 'năm'][g.evidence.length] ?? String(g.evidence.length), rules: [] },
      's.books': { text: joinVi(g.books), rules: [] }, 's.cond': { text: g.evidence[0].chartCondition, rules: [] },
    }))));

    // sát stars shared by several qualifier readings of the career palace
    const qe = this.lists.get('qualifier_quan')!.flatMap(c => c.grounds.flatMap(g => g.evidence));
    const satTp = (a.slots['quan.sat_tp'] || '').split(/, | và /).map(x => x.split(' ở ')[0]).filter(Boolean);
    const count = new Map<string, number>();
    for (const e of qe) for (const s of new Set([...e.presentStars, ...(/sát tinh/.test(e.chartCondition) ? satTp : [])])) if (SAT_SET.has(s)) count.set(s, (count.get(s) ?? 0) + 1);
    const shared = [...count].filter(([, n]) => n >= 2).map(([s]) => s);
    this.set('q.sat_shared', qe.length >= 2 && shared.length ? `${joinVi(shared)} trong khung đọc của Quan Lộc` : '', qe.map(e => e.rule.id));

    // dominance verdicts: the first pair is argued in full, later pairs with the same verdict refer back to it; a same-book note goes with its pair
    let first = true, noted = false;
    this.items.set('dominance', a.dominance.map(d => {
      const qq = d.qualifier.grounds.flatMap(g => g.evidence).find(e => d.sharedStars.some(st => e.presentStars.includes(st))) ?? d.qualifier.grounds[0].evidence[0];
      const qcond = qq.chartCondition;
      let verdict: string;
      if (d.verdict === 'qualified_base' && first) verdict = `Theo các tiêu chí đó, câu thuận về ${joinVi(d.sharedStars) || 'cấu hình của cung'} vẫn đứng như mô tả tiềm năng của cung, còn câu hạn chế cho biết điều kiện mà lá số này thỏa (${qcond}), nên nó được đọc như một điều chỉnh mức độ chứ không phải lời phủ định.`;
      else if (d.verdict === 'qualified_base') verdict = `Cặp này theo cùng lối đọc: ${joinVi(d.sharedStars) || 'chính tinh'} cho tiềm năng, còn điều kiện “${qcond}” là phần điều chỉnh.`;
      else verdict = 'Theo các tiêu chí đó, không bên nào chi phối bên nào, nên bản luận giữ cả hai như hai chiều cùng tồn tại.';
      const criteria = first ? d.criteria.join('; ') : d.criteria.slice(0, 2).join(', ');
      first = false;
      let note = '';
      if (d.sameBook && d.sharedStars.length) {
        const be = d.base.grounds[0].evidence[0], qe0 = d.qualifier.grounds.flatMap(g => g.evidence).find(e => e.books.some(bk => be.books.includes(bk)));
        if (qe0 && !noted) note = ` ${be.books.join(', ')} tự đặt hai câu này trong cùng mục bàn về ${joinVi(d.sharedStars)} ở cung Quan Lộc (${[...new Set([...be.cites, ...qe0.cites])].map(citeVi).join('; ')}), mỗi câu cho một điều kiện; lá số thỏa cả hai nên cả hai cùng hiệu lực.`;
        else if (qe0) note = ` Ở đây ${be.books.join(', ')} cũng ghi hai câu trong cùng mục về ${joinVi(d.sharedStars)}.`;
        if (qe0) noted = true;
      }
      return { 'd.base': { text: d.base.quotes[0], rules: d.base.rules }, 'd.qual': { text: qq.core, rules: d.qualifier.rules },
        'd.criteria': { text: criteria, rules: [] }, 'd.verdict': { text: verdict + note, rules: [] } };
    }));
    this.set('d.same_book_note', '');

    // cross-palace items
    this.items.set('cross', a.cross.slice(0, 3).map(x => {
      const e = x.claim.grounds[0].evidence[0];
      const byPal = new Map<string, string[]>();
      for (const d of x.deps) byPal.set(d.palace, [...(byPal.get(d.palace) ?? []), d.star]);
      const deps = byPal.size ? joinVi([...byPal].map(([p, st]) => `${joinVi(st)} nằm ở cung ${p}`)) : e.chartCondition;
      return { 'x.from': { text: x.claim.palace, rules: [] }, 'x.books': { text: joinVi(e.books), rules: [] }, 'x.quote': { text: e.core, rules: x.claim.rules },
        'x.cite': { text: citesOf(x.claim).join('; '), rules: [] }, 'x.deps': { text: deps, rules: [] },
        'x.dep_palaces': { text: joinVi([...new Set(x.deps.map(d => `cung ${d.palace}`))]) || 'các cung tam phương', rules: [] } };
    }));
    this.lists.set('cross', a.cross.slice(0, 3).map(x => x.claim));

    // group coherence: the planner sets group.same only when Khảo Luận's Tử – Phủ – Vũ – Tướng rule fired for Mệnh and the career palace's
    // chính tinh all belong to that group
    this.set('group.same', a.slots['group.same'] ?? '', a.slots['group.rule'] ? [a.slots['group.rule']] : []);

    // tensions sharing their limiting side are told once: "A, B đều ngược chiều với N"
    const byNeg = new Map<string, typeof a.tensions>();
    for (const t of a.tensions) byNeg.set(t.neg.id, [...(byNeg.get(t.neg.id) ?? []), t]);
    this.items.set('tension', [...byNeg.values()].slice(0, 3).map(ts => {
      const ne = ts[0].neg.grounds[0].evidence[0], pes = ts.map(t => t.pos.grounds[0].evidence[0]);
      const palaces = [...new Set([...ts.map(t => t.pos.palace), ts[0].neg.palace])];
      const refine = ts.every(t => t.kind === 'refinement');
      const verdict = refine
        ? 'câu hạn chế có điều kiện cụ thể hơn và lá số thỏa điều kiện ấy, nên nó điều chỉnh chứ không xóa câu thuận'
        : `chúng đứng trên những dữ kiện khác nhau (${joinVi([...new Set(pes.map(e => e.chartCondition))])} so với ${ne.chartCondition}) và đều thỏa; sách không xếp thứ tự, nên bản luận giữ cả hai chiều`;
      return { 't.pos': { text: joinVi(pes.map(e => e.core)), rules: ts.flatMap(t => t.pos.rules) }, 't.neg': { text: ne.core, rules: ts[0].neg.rules },
        't.where': { text: palaces.length === 1 ? `cùng ở cung ${palaces[0]}` : `ở ${joinVi(palaces.map(p => 'cung ' + p))}`, rules: [] }, 't.verdict': { text: verdict, rules: [] } };
    }));
    // timing conflict (early vs late readings)
    const early = a.timingConflict.early, late = a.timingConflict.late;
    this.set('t.late', late.length ? '1' : '');
    this.set('dh.quan_conflict', a.slots['dh.quan_conflict'] ? 'Hai câu này ngược chiều nhau trên cùng một đại hạn và cùng khớp điều kiện, nên bản luận không kết luận chặng ấy đi lên hay đi xuống.' : '');
    this.set('t.conflict', early.length && late.length
      ? `Hai câu về nhịp này ngược chiều nhau: “${early[0].quotes[0]}” đứng trên ${early[0].grounds[0].evidence[0].chartCondition}, còn “${late[0].quotes[0]}” đứng trên ${late[0].grounds[0].evidence[0].chartCondition}. Hai căn cứ khác nhau và đều thỏa; sách không xếp thứ tự giữa chúng, nên bản luận giữ cả hai thay vì chọn một.` : '',
      [...early, ...late].flatMap(c => c.rules));

    // limits
    this.set('lim.drafts', joinVi(a.excluded.drafts.map(d => `“${d.text.split(' (')[0]}”`)), a.excluded.drafts.map(d => d.rule));
    this.set('lim.drafts_n', ['', 'một', 'hai', 'ba', 'bốn'][a.excluded.drafts.length] ?? String(a.excluded.drafts.length));
    this.set('lim.drafts_pron', a.excluded.drafts.length === 1 ? 'nó' : 'chúng');
    this.set('lim.scope', joinVi(a.excluded.scopeNotes.map(n => `“${n.text.split(' (')[0]}”`)), a.excluded.scopeNotes.map(n => n.rule));

    // synthesis
    const np = (cs: Claim[]) => joinVi([...new Set(cs.map(c => this.k.concepts.concepts.find(x => x.id === c.concept)?.short ?? c.quotes[0]))]);
    this.set('syn.base', a.lists.base.length ? `${np(a.lists.base)} (${joinVi(a.lists.base.map(c => `“${c.quotes[0]}”`))})` : '', a.lists.base.flatMap(c => c.rules));
    const qq = this.lists.get('qualifier_quan')!;
    this.set('syn.qual', qq.length ? `${shared.length ? joinVi(shared) + ' trong cung' : 'các điều kiện hạn chế'} (${joinVi(qq.map(c => `“${c.quotes[0]}”`))})` : '', qq.flatMap(c => c.rules));
    // group by palace so each palace is named once ("“a” và “b” ở Mệnh", not "“a” ở Mệnh và “b” ở Mệnh")
    const byPal = new Map<string, string[]>();
    for (const x of a.cross) byPal.set(x.claim.palace, [...(byPal.get(x.claim.palace) ?? []), `“${x.claim.quotes[0]}”`]);
    this.set('syn.cross', a.cross.length ? joinVi([...byPal].map(([pal, qs]) => `${joinVi(qs)} ở ${pal}`)) : '', a.cross.flatMap(x => x.claim.rules));
    this.set('syn.timing', late.length ? `sách nghiêng về thành tựu đến muộn${a.slots['dh.quan'] ? `, và chặng đại hạn qua Quan Lộc ở ${a.slots['dh.quan']} tuổi mụ` : ''}${early.length ? ', dù có một câu ngược chiều' : ''}` : '', late.flatMap(c => c.rules));
    const refl = this.k.ontology?.facets?.['career.trajectory']?.reflection;
    this.set('syn.reflect', a.dominance.length && refl ? refl : '');
  }

  private listText(name: string): Slot {
    const all = this.lists.get(name) ?? [], cap = Math.max(1, Math.round((CAPS[name] ?? 4) * this.capScale)), cs = all.slice(0, cap);
    const withCond = !['base', 'support'].includes(name);
    const seen = new Set<string>();
    const items = cs.map(c => claimItem(c, withCond || c.grounds.length > 1).replace(/ tại (Quan Lộc|Mệnh|Thiên Di|Tài Bạch|Phu Thê)/g, (m, p) => {
      if (seen.has(p)) return ''; seen.add(p); return m;
    }));
    const more = all.length - cs.length;
    return { text: items.join('; ') + (more > 0 ? `; cùng ${more} câu khác cùng chiều, xem trong danh sách chi tiết` : ''), rules: cs.flatMap(c => c.rules) };
  }

  /** Fill {slot}, {list:name} and optional {?slot|text} segments; returns null when a required slot is missing or empty. */
  fill(tpl: string, item?: Record<string, Slot>, inner = false): { text: string; rules: string[] } | null {
    const rules: string[] = [];
    const get = (key: string): Slot | undefined => item?.[key] ?? (key.startsWith('list:') ? this.listText(key.slice(5)) : this.slots.get(key));
    let t = tpl.replace(/\{\?([\w.:]+)\|((?:[^{}]|\{[^{}]*\})*)\}/g, (_, key: string, body: string) => {
      const s = get(key); if (!s || !s.text) return '';
      const part = this.fill(body, item, true); if (!part) return '';
      rules.push(...s.rules, ...part.rules); return part.text;
    });
    let missing = false;
    t = t.replace(/\{([\w.:]+)\}/g, (_, key: string) => { const s = get(key); if (!s || !s.text) { missing = true; return ''; } rules.push(...s.rules); return s.text; });
    if (missing) return null;
    return { text: inner ? t : t.replace(/\s+([,.;])/g, '$1').replace(/\s{2,}/g, ' ').trim(), rules };
  }

  cond(c: ModuleCond | undefined): boolean {
    if (!c) return true;
    if ('all' in c) return c.all.every(x => this.cond(x));
    if ('any' in c) return c.any.some(x => this.cond(x));
    if ('not' in c) return !this.cond(c.not);
    if ('list' in c) return (this.lists.get(c.list)?.length ?? this.items.get(c.list)?.length ?? 0) >= (c.min ?? 1);
    if ('slot' in c) { const v = this.slots.get(c.slot)?.text ?? ''; return c.truthy === false ? !v : c.eq !== undefined ? v === c.eq : !!v; }
    return false;
  }

  render(modules: ContentModule[]): Paragraph[] {
    const recent: string[] = [], out: Paragraph[] = [];
    for (const m of [...modules].sort((x, y) => x.order - y.order)) {
      if (m.status === 'retired' || !this.cond(m.when)) continue;
      const sentences: Sentence[] = [];
      for (const p of m.passages) {
        if (!this.cond(p.when)) continue;
        const items = p.each ? (this.items.get(p.each) ?? []) : [undefined];
        items.forEach((item, idx) => {
          const filled = this.pick(m, p, idx, item, recent);
          if (!filled) return;
          const cites = (p.cites ?? []).map(c => this.fill(c)?.text ?? c).filter(Boolean).map(citeVi);
          for (const text of splitSentences(filled.text)) {
            sentences.push({ text, basis: p.basis, kind: p.kind ?? 'claim', module: m.id, passage: p.id, rules: [...new Set(filled.rules)], cites });
            recent.push(opener(text));
          }
        });
      }
      if (sentences.length) out.push({ module: m.id, role: m.role, title: m.title, sentences, text: sentences.map(s => s.text).join(' ') });
    }
    return out;
  }

  private pick(m: ContentModule, p: Passage, idx: number, item: Record<string, Slot> | undefined, recent: string[]) {
    const pool = idx > 0 && p.followups?.length ? p.followups : p.variants;
    const n = pool.length, start = hash(`${this.seed}|${m.id}|${p.id}|${idx}`) % n;
    let fallback: ReturnType<Realizer['fill']> = null;
    for (let i = 0; i < n; i++) {
      const v = pool[(start + i) % n], f = this.fill(v, item);
      if (!f) continue;
      fallback ??= f;
      if (!recent.slice(-3).includes(opener(f.text))) return f;
    }
    return fallback;
  }
}

const CAPS: Record<string, number> = { base: 4, support: 3, qualifier_quan: 4, qualifier_other: 2, env_pos: 2, env_neg: 2, timing: 3, work_style: 2 };
const SAT_SET = new Set(['Kình Dương', 'Đà La', 'Hỏa Tinh', 'Linh Tinh', 'Địa Không', 'Địa Kiếp']);

/** Sentence split that never cuts inside quotes or parentheses. */
export function splitSentences(text: string): string[] {
  const out: string[] = []; let depth = 0, q = false, cur = '';
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]; cur += ch;
    if (ch === '(') depth++; else if (ch === ')') depth = Math.max(0, depth - 1);
    else if (ch === '“') q = true; else if (ch === '”') q = false;
    else if ((ch === '.' || ch === '?') && !depth && !q && (text[i + 1] === ' ' || i === text.length - 1)) { out.push(cur.trim()); cur = ''; }
  }
  if (cur.trim()) out.push(cur.trim());
  return out.filter(Boolean);
}
