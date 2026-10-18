// Deterministic narrative generator: argument graph + editorial modules -> Vietnamese chapter.
// Slots are filled only from the argument graph (chart facts, fired verified rules and their pages); a passage whose slot is empty or
// unknown is skipped, never padded. Variant choice is a hash of (chart, module, passage) that skips variants whose opening words were
// used in the last sentences, so the same chart always reads the same and different charts do not read like one template.
// Every slot value carries the rules it came from; after sentence splitting each sentence keeps only the rules of the slot values it
// actually contains (sentence-level provenance).
import { joinVi, condText, type Evidence } from './semantic.ts';
import { mergeCites, type ArgumentGraph, type Claim, type CrossLink, type Dominance } from './planner.ts';
import { SAT } from './graph.ts';
import type { Basis, ContentModule, Knowledge, ModuleCond, Passage } from './types.ts';

export interface Sentence { text: string; basis: Basis; kind: string; module: string; passage: string; rules: string[]; cites: string[] }
export interface Paragraph { module: string; role: string; title: string; sentences: Sentence[]; text: string }
type Slot = { text: string; rules: string[] };
type Filled = { text: string; rules: string[]; spans: Slot[] };

const BOOK: Record<string, string> = { TH: 'Thực Hành', KL: 'Khảo Luận', TT: 'Toàn Thư' };
export const citeVi = (c: string) => { const m = c.match(/^(TH|KL|TT)\s+(?:pp?\.)?\s*(.+)$/); return m ? `${BOOK[m[1]]} tr.${m[2].replace(/-/g, '–')}` : c; };
const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : s;
const q = (s: string) => `“${s}”`;
const NUM = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu'];

function hash(s: string): number { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const opener = (t: string) => t.replace(/[^\p{L}\p{N} ]/gu, ' ').trim().split(/\s+/).slice(0, 2).join(' ').toLowerCase();
const evOf = (c: Claim) => c.grounds.flatMap(g => g.evidence);
const citesOf = (es: Evidence[]) => mergeCites([...new Set(es.flatMap(e => e.cites))].map(citeVi));

export class Realizer {
  slots = new Map<string, Slot>(); lists = new Map<string, Claim[]>(); items = new Map<string, Array<Record<string, Slot>>>();
  a: ArgumentGraph; k: Knowledge; seed: string; capScale: number; focus: string;
  constructor(a: ArgumentGraph, k: Knowledge, seed: string, capScale = 1) { this.a = a; this.k = k; this.seed = seed; this.capScale = capScale; this.focus = a.focus; this.prepare(); }

  private set(key: string, text: string, rules: string[] = []) { this.slots.set(key, { text, rules }); }
  private short(c: Claim) { return this.k.concepts.concepts.find(x => x.id === c.concept)?.short ?? c.quotes[0]; }

  /** One list item: each distinct quote once, with the condition(s) that carry it; the palace is not repeated when it is `home`. */
  private item(c: Claim, withCond: boolean, home: string | undefined): { text: string; cite: string } {
    const groups: Array<{ quotes: string[]; conds: string[] }> = [];
    // a condition that only restates the focus palace's own chính tinh (already named in the opening paragraph) is not repeated
    const fm = new Set(this.a.slots['f.majors'] ? this.a.slots['f.majors'].split(/, | và /) : []);
    const bare = (e: Evidence) => home === this.focus && e.cond.palace === this.focus && e.cond.own.length > 0 && e.cond.own.every(s => fm.has(s) && !e.cond.dig[s])
      && !e.cond.hoa.length && !e.cond.opp.length && !e.cond.tp.filter(s => !e.cond.own.includes(s)).length && !e.cond.nb.length && !e.cond.branch && !e.cond.tt.length && !e.cond.extra.length;
    for (const g of c.grounds) {
      const quotes = [...new Set(g.evidence.map(e => e.core))], cond = bare(g.evidence[0]) ? '' : condText(g.evidence[0].cond, home);
      const hit = groups.find(x => x.quotes.join('|') === quotes.join('|'));
      const sameCond = groups.find(x => x.conds.length === 1 && x.conds[0] === cond && cond);
      if (hit) { if (cond && !hit.conds.includes(cond)) hit.conds.push(cond); }
      else if (sameCond) sameCond.quotes.push(...quotes.filter(x => !sameCond.quotes.includes(x)));
      else groups.push({ quotes, conds: cond ? [cond] : [] });
    }
    const parts = (home === this.focus ? groups : groups.slice(0, 2)).map(({ quotes, conds }) => {
      const qs = joinVi(quotes.map(q));
      if (!withCond || !conds.length) return qs;
      return `${qs} khi ${conds.length > 1 ? conds.slice(0, -1).join('; ') + ', và cả khi ' + conds[conds.length - 1] : conds[0]}`;
    });
    return { text: joinVi(parts), cite: citesOf(evOf(c)) };
  }

  private listText(name: string): Slot {
    const all = this.lists.get(name) ?? [], n = Math.max(1, Math.round((CAPS[name] ?? 4) * this.capScale)), cs = all.slice(0, n);
    const home = HOME[name]?.(this.a);
    const withCond = !['base_plain'].includes(name);
    const rendered0 = cs.map(c => this.item(c, withCond, home));
    const rendered: Array<{ text: string; cite: string }> = [];
    for (const r of rendered0) {
      const m = r.text.match(/^((?:“[^”]*”(?:, | và )?)+) khi (.+)$/), prev = rendered[rendered.length - 1];
      const pm = prev?.text.match(/^((?:“[^”]*”(?:, | và )?)+) khi (.+)$/);
      if (m && pm && m[2] === pm[2]) { prev.text = `${pm[1].replace(/ và (“[^”]*”)$/, ', $1')} và ${m[1]} khi ${m[2]}`; prev.cite = mergeCites([prev.cite, r.cite].filter(Boolean).flatMap(x => x.split('; '))); }
      else rendered.push({ ...r });
    }
    // a citation shared by consecutive items is written once, after the last of them
    const items = rendered.map((r, i) => `${r.text}${r.cite && rendered[i + 1]?.cite !== r.cite ? ` (${r.cite})` : ''}`);
    const more = all.length - cs.length;
    const kind = name.startsWith('qualifier') || name === 'env_neg' ? 'hạn chế' : name === 'timing' ? 'về nhịp' : 'thuận';
    return { text: items.join('; ') + (more > 0 ? `; và ${NUM[more] ?? more} câu ${kind} khác trong danh sách chi tiết` : ''), rules: cs.flatMap(c => c.rules) };
  }

  private prepare() {
    const a = this.a, F = this.focus;
    for (const [k, v] of Object.entries(a.slots)) this.set(k, v);
    const L = (name: string, cs: Claim[]) => this.lists.set(name, cs);
    L('base', a.lists.base); L('support', a.lists.support); L('work_style', a.lists.work_style);
    L('qualifier_f', a.lists.qualifier.filter(c => c.palace === F)); L('qualifier_other', a.lists.qualifier.filter(c => c.palace !== F));
    L('environment', a.lists.environment);
    L('env_pos', a.lists.environment.filter(c => c.polarity !== '-')); L('env_neg', a.lists.environment.filter(c => c.polarity === '-'));
    L('timing', a.lists.timing); L('generic', a.lists.generic ?? []);
    L('dominance', a.dominance.map(d => d.qualifier));

    // claims whose several book sentences stand on ONE ground (the dedup the reader should see)
    this.items.set('shared_ground', a.claims.filter(c => c.role === 'base' || c.role === 'support').flatMap(c => c.grounds.filter(g => new Set(g.evidence.map(e => e.core)).size >= 2).map(g => {
      const cores = [...new Set(g.evidence.map(e => e.core))];
      return { 's.quotes': { text: joinVi(cores.map(q)), rules: g.evidence.map(e => e.rule.id) }, 's.n': { text: NUM[cores.length] ?? String(cores.length), rules: [] },
        's.books': { text: joinVi(g.books), rules: [] }, 's.cond': { text: condText(g.evidence[0].cond), rules: [] } };
    })));

    // sát stars shared by several qualifier readings of the focus palace
    const qe = this.lists.get('qualifier_f')!.flatMap(evOf);
    const count = new Map<string, number>();
    for (const e of qe) for (const s of new Set(e.presentStars)) if (SAT.includes(s)) count.set(s, (count.get(s) ?? 0) + 1);
    const shared = [...count].filter(([, n]) => n >= 2).map(([s]) => s);
    this.set('q.sat_shared', qe.length >= 2 && shared.length ? `${joinVi(shared)} trong khung đọc của ${F}` : '', qe.map(e => e.rule.id));

    // dominance: the first pair argued in full, later pairs by their operative criterion only
    this.items.set('dominance', a.dominance.map((d, i) => ({ 'd.text': { text: this.domText(d, i === 0, i > 0 && a.dominance.slice(0, i).some(o => o.sameBook && o.books.join() === d.books.join())), rules: [...d.bases.flatMap(b => b.rules), ...d.qualifier.rules] } })));

    // tensions, grouped by their limiting side
    // 'both hold' tensions of one palace are told in one sentence with one shared verdict; refinements each get their own
    const groupsT: Array<typeof a.tensions> = [];
    for (const t of a.tensions) {
      const g = t.kind === 'both_hold' ? groupsT.find(x => x[0].kind === 'both_hold') : undefined;
      if (g) g.push(t); else groupsT.push([t]);
    }
    this.items.set('tension', groupsT.slice(0, 3).map(ts => ({ 't.text': { text: ts.length === 1 ? this.tensionText(ts[0]) : this.tensionGroup(ts), rules: ts.flatMap(t => [...t.pos.flatMap(c => c.rules), ...t.negs.flatMap(c => c.rules)]) },
      't.where': { text: ts.length > 1 && new Set(ts.map(t => t.neg.palace)).size > 1 ? 'Ngoài ra' : this.where(ts[0]), rules: [] }, 't.where_l': { text: this.where(ts[0], true), rules: [] } })));

    // cross-palace items: a quote with the stars it NEEDS; link items: in-scope readings of a linked palace that stand on it alone
    const crossItem = (x: CrossLink): Record<string, Slot> => {
      const e = x.evidence, by = (ds: typeof x.deps) => { const m = new Map<string, string[]>(); for (const d of ds) m.set(d.palace, [...(m.get(d.palace) ?? []), d.star]); return joinVi([...m].map(([p, st]) => `${joinVi(st)} ở cung ${p}`)); };
      return { 'x.from': { text: x.claim.palace, rules: [] }, 'x.books': { text: joinVi(e.books), rules: [] }, 'x.quote': { text: e.core, rules: [e.rule.id] },
        'x.cite': { text: citesOf([e]), rules: [] }, 'x.deps': { text: by(x.deps), rules: [] }, 'x.support': { text: by(x.support), rules: [] },
        'x.cond': { text: condText(e.cond, x.claim.palace), rules: [] } };
    };
    this.items.set('cross', a.cross.slice(0, Math.max(1, Math.round(3 * this.capScale))).map(crossItem));
    this.items.set('link', a.links.slice(0, Math.max(1, Math.round(2 * this.capScale))).map(crossItem));
    this.set('group.same', a.slots['group.same'] ?? '', a.slots['group.rule'] ? [a.slots['group.rule']] : []);

    // timing conflict and lean
    const T = a.timing;
    if (T.early.length && T.late.length) {
      const ee = evOf(T.early[0])[0], le = evOf(T.late[0])[0];
      const head = `Về nhịp thời gian, sách có hai câu ngược chiều nhau: ${q(ee.core)} khi ${condText(ee.cond)} (${citesOf([ee])}), và ${q(le.core)} khi ${condText(le.cond)} (${citesOf([le])}).`;
      const tail = T.leanReason === 'specific'
        ? ` Câu về nhịp ${T.lean === 'late' ? 'sớm' : 'muộn'} dựa vào một thế chung theo năm sinh, còn câu về nhịp ${T.lean === 'late' ? 'muộn' : 'sớm'} dựa vào sao riêng của lá số này; theo quy ước ưu tiên điều kiện cụ thể, bản luận nghiêng về nhịp ${T.lean === 'late' ? 'muộn' : 'sớm'}, nhưng vẫn ghi cả hai.`
        : ' Cả hai đều dựa vào dữ kiện riêng của lá số và sách không xếp thứ tự giữa chúng, nên bản luận giữ cả hai thay vì chọn một.';
      this.set('t.conflict', head + tail, [...T.early, ...T.late].flatMap(c => c.rules));
    } else this.set('t.conflict', '');
    this.set('dh.f_conflict', a.slots['dh.f_conflict'] ? 'Hai câu này ngược chiều nhau trên cùng một đại hạn và cùng khớp điều kiện, nên bản luận không kết luận chặng ấy đi lên hay đi xuống.' : '');

    // limits
    const dq = a.excluded.drafts.filter(d => !d.neg).slice(0, 3), dn = a.excluded.drafts.length - dq.length;
    this.set('lim.drafts', joinVi([...dq.map(d => q(d.text)), ...(dn ? [`${NUM[dn] ?? dn} câu${dq.length ? ' khác' : ''} không trích ở đây`] : [])]), a.excluded.drafts.map(d => d.rule));
    this.set('lim.drafts_n', NUM[a.excluded.drafts.length] ?? String(a.excluded.drafts.length));
    this.set('lim.drafts_pron', a.excluded.drafts.length === 1 ? 'nó' : 'chúng');
    this.set('lim.scope', joinVi(a.excluded.scopeNotes.map(n => q(n.text))), a.excluded.scopeNotes.map(n => n.rule));

    // synthesis: concepts, not re-quoted sentences; the verdict of the first dominance pair; a timing lean only when the planner has one
    const shorts = (cs: Claim[]) => joinVi([...new Set(cs.map(c => this.short(c)))]);
    this.set('syn.base', a.lists.base.length ? shorts(a.lists.base) : '', a.lists.base.flatMap(c => c.rules));
    this.set('syn.support', a.lists.support.length ? shorts(a.lists.support.slice(0, 2)) : '', a.lists.support.slice(0, 2).flatMap(c => c.rules));
    const d0 = a.dominance[0];
    const qq = this.lists.get('qualifier_f')!;
    const qualWhat = shared.length ? `${joinVi(shared)} trong cung` : qq.length ? joinVi(qq.slice(0, 2).map(c => q(c.quotes[0]))) : '';
    let verdict = '';
    if (d0) {
      const qualWhat = shared.length ? `${joinVi(shared)} trong cung, yếu tố chung của các câu hạn chế,` : d0.relation === 'sat_qualifier' && d0.addedSat.length ? `${joinVi(d0.addedSat.map(s => s.split(' (')[0]))} (qua câu ${q(d0.qualEvidence.core)})` : q(d0.qualEvidence.core);
      verdict = d0.relation === 'sat_qualifier' ? `${qualWhat} hạ mức độ của tiềm năng ấy chứ không xóa nó`
        : d0.relation === 'specific_qualifier' ? `lá số rơi vào trường hợp riêng mà sách tách ra (${condText(d0.qualEvidence.cond, F)}), nên cách đọc hạn chế được đặt lên trước`
        : d0.relation === 'specific_base' ? `câu thuận là trường hợp riêng sát với lá số hơn, còn ${qualWhat} là mặt chung cần để ý`
        : `${qualWhat} cùng tồn tại bên cạnh, sách không xếp thứ tự`;
    } else if (qualWhat) verdict = `${qualWhat} là phần cần cân nhắc`;
    this.set('syn.verdict', verdict, qq.flatMap(c => c.rules));
    const xs = [...a.cross.map(x => x.claim), ...a.links.map(x => x.claim)].filter((c, i, arr) => arr.indexOf(c) === i);
    const byPal = new Map<string, Claim[]>();
    for (const c of xs) byPal.set(c.palace, [...(byPal.get(c.palace) ?? []), c]);
    const palText = ([p, cs]: [string, Claim[]]) => {
      const pos = [...new Set(cs.filter(c => c.polarity !== '-').map(c => this.short(c)))].slice(0, 2), neg = [...new Set(cs.filter(c => c.polarity === '-').map(c => this.short(c)))].slice(0, 1);
      return `cung ${p} góp thêm ${pos.length ? joinVi(pos) : ''}${pos.length && neg.length ? ', nhưng cũng có ' : ''}${neg.length ? joinVi(neg) : ''}`;
    };
    const contrib = new Map<string, string[]>();
    for (const e of [...byPal]) { const t = palText(e).replace(/^cung \S+( \S+)? góp thêm /, ''); contrib.set(t, [...(contrib.get(t) ?? []), e[0]]); }
    this.set('syn.cross', xs.length ? [...contrib].map(([t, ps], i) => `${joinVi(ps.map(p => 'cung ' + p))} ${i ? 'cũng góp' : ps.length > 1 ? 'cùng góp thêm' : 'góp thêm'} ${t}`).join('; ') : '', xs.flatMap(c => c.rules));
    const dh = a.slots['dh.f'] ? `, còn chặng đại hạn qua ${F} là ${a.slots['dh.f']} tuổi mụ` : '';
    const tim = T.lean && T.leanReason === 'one_side' ? `${T.early.length + T.late.length > 1 ? 'các câu sách đều chỉ về' : 'câu sách duy nhất chỉ về'} ${T.lean === 'late' ? 'thành tựu đến muộn' : 'thành tựu đến sớm'}`
      : T.lean ? `bản luận nghiêng về nhịp ${T.lean === 'late' ? 'muộn' : 'sớm'} theo quy ước ưu tiên điều kiện cụ thể`
      : T.early.length && T.late.length ? 'sách có cả câu về nhịp sớm lẫn nhịp muộn và không phân định'
      : T.leanReason === 'generic_only' ? 'câu sách về nhịp chỉ là một thế chung theo năm sinh, nên bản luận không dựa vào đó để nói sớm hay muộn' : '';
    this.set('syn.timing', tim ? tim + dh : '', [...T.early, ...T.late].flatMap(c => c.rules));
  }

  private where(t: { neg: Claim }, lower = false): string { return `${lower ? 'ở' : 'Ở'} cung ${t.neg.palace}`; }

  private domText(d: Dominance, first: boolean, bookAlreadyNoted: boolean): string {
    const F = this.focus, B = joinVi([...new Set(d.bases.map(b => b.quotes[0]))].map(q)), Q = q(d.qualEvidence.core), S = joinVi(d.sharedStars);
    const qcond = condText(d.qualEvidence.cond, F);
    const sats = d.addedSat;
    if (!first) {
      const why = d.relation === 'sat_qualifier' ? `câu sau thêm ${joinVi(sats)} vào cùng ${S || 'cấu hình'}, nên cũng là mức điều chỉnh`
        : d.relation === 'specific_qualifier' ? `câu sau là trường hợp riêng (${qcond}) nên được đọc trước`
        : d.relation === 'specific_base' ? 'câu trước là trường hợp riêng nên được đọc trước'
        : 'điều kiện không chứa nhau, nên giữ cả hai';
      return `Đặt ${B} cạnh ${Q}${d.sameBook && !bookAlreadyNoted ? ` (cùng ${d.books.join(', ')})` : ''}: ${why}.`;
    }
    const src = d.sameSection ? ` và cùng nằm trong một mục của ${d.books.join(', ')} (${mergeCites(d.cites.map(citeVi))})`
      : d.sameBook ? `, cùng do ${d.books.join(', ')} ghi` : d.books.length > 1 ? `, từ ${joinVi(d.books)}` : '';
    const head = d.bases.length > 1
      ? `Các câu thuận ${[...new Set(d.bases.map(b => b.quotes[0]))].map(q).join(', ')} và câu hạn chế ${Q} ${S ? `cùng nói về ${S}` : 'cùng nói về cung này'}${src}, nên không thể coi bên này bác bỏ bên kia.`
      : `${cap(B)} và ${Q} ${S ? `cùng nói về ${S}` : 'cùng nói về cung này'}${src}, nên không thể coi câu này bác bỏ câu kia.`;
    const body = d.relation === 'sat_qualifier'
      ? ` Câu hạn chế giữ nguyên ${S || 'chính tinh'} và chỉ thêm sát tinh — ${joinVi(sats)} — mà lá số này có; theo quy ước ấy, câu thuận là tiềm năng của cung, còn câu hạn chế cho biết tiềm năng ấy bị kéo xuống đến đâu.`
      : d.relation === 'specific_qualifier'
      ? ` Điều kiện của câu hạn chế (${qcond}) chứa trọn điều kiện của câu thuận và thêm dữ kiện, tức lá số rơi vào trường hợp riêng mà sách tách ra; theo quy ước ấy, câu hạn chế là cách đọc sát hơn cho lá số này, còn câu thuận mô tả cấu hình nói chung.`
      : d.relation === 'specific_base'
      ? ` Điều kiện của câu thuận chứa trọn điều kiện của câu hạn chế và thêm dữ kiện, nên theo quy ước ấy câu thuận là cách đọc sát hơn; câu hạn chế nhắc mặt chung cần để ý.`
      : ` Hai điều kiện không chứa nhau và lá số thỏa cả hai, nên bản luận giữ cả hai chiều.`;
    return head + body;
  }

  private tensionGroup(ts: Array<{ pos: Claim[]; neg: Claim; negs: Claim[]; kind: string }>): string {
    const multi = new Set(ts.map(t => t.neg.palace)).size > 1, par = (s: string) => s ? ` (${s})` : '';
    const pairs = ts.slice(0, 3).map(t => {
      const home = t.neg.palace, pe = t.pos.map(c => evOf(c)[0]), nes = t.negs.map(c => evOf(c)[0]);
      return `${multi ? `ở cung ${home}, ` : ''}${joinVi(pe.map(e => q(e.core)))}${par(condText(pe[0].cond, home))} đối với ${joinVi(nes.map(e => q(e.core)))}${par(joinVi([...new Set(nes.map(e => condText(e.cond, home)))].filter(Boolean)))}`;
    });
    return `có ${NUM[pairs.length] ?? pairs.length} chỗ trái chiều — ${pairs.join('; ')}. Mỗi cặp đứng trên những dữ kiện khác nhau và cùng thỏa; sách không xếp thứ tự, nên bản luận giữ cả hai chiều`;
  }

  private tensionText(t: { pos: Claim[]; neg: Claim; negs: Claim[]; kind: string }): string {
    const pe = t.pos.map(c => evOf(c)[0]), nes = t.negs.map(c => evOf(c)[0]), ne = nes[0];
    const home = t.neg.palace;
    const par = (s: string) => s ? ` (${s})` : '';
    const P = joinVi(pe.map(e => q(e.core))), N = joinVi(nes.map(e => q(e.core))), pc = condText(pe[0].cond, home), nc = joinVi([...new Set(nes.map(e => condText(e.cond, home)))].filter(Boolean));
    if (t.kind === 'neg_refines') return `${N}${par(nc)} là trường hợp hẹp hơn của dữ kiện mà ${P} nói chung, nên được đọc như phần điều chỉnh`;
    if (t.kind === 'pos_refines') return `${P}${par(pc)} là trường hợp hẹp hơn của dữ kiện mà ${N}${par(nc)} nói chung, nên ở lá số này câu thuận sát hơn`;
    return `${P}${par(pc)} và ${N}${par(nc)} đứng trên những dữ kiện khác nhau và cùng thỏa; sách không xếp thứ tự, nên bản luận giữ cả hai chiều`;
  }

  /** Fill {slot}, {list:name} and optional {?slot|text} segments; returns null when a required slot is missing or empty. */
  fill(tpl: string, item?: Record<string, Slot>, inner = false): Filled | null {
    const rules: string[] = [], spans: Slot[] = [];
    const get = (key: string): Slot | undefined => item?.[key] ?? (key.startsWith('list:') ? this.listText(key.slice(5)) : this.slots.get(key));
    let t = tpl.replace(/\{\?([\w.:]+)\|((?:[^{}]|\{[^{}]*\})*)\}/g, (_, key: string, body: string) => {
      const s = get(key); if (!s || !s.text) return '';
      const part = this.fill(body, item, true); if (!part) return '';
      rules.push(...s.rules, ...part.rules); spans.push(...part.spans); return part.text;
    });
    let missing = false;
    t = t.replace(/\{([\w.:]+)\}/g, (_, key: string) => { const s = get(key); if (!s || !s.text) { missing = true; return ''; } rules.push(...s.rules); if (s.rules.length) spans.push(s); return s.text; });
    if (missing) return null;
    return { text: inner ? t : t.replace(/\s+([,.;])/g, '$1').replace(/\s{2,}/g, ' ').trim(), rules, spans };
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
    for (const m of [...modules].sort((x, y) => x.order - y.order || x.id.localeCompare(y.id))) {
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
            // sentence-level provenance: the rules of the slot values this sentence contains (a sentence of a book passage that names no
            // slot value keeps the passage's rules, so no book sentence is left without its source)
            const own = [...new Set(filled.spans.filter(s => s.text && (text.includes(s.text) || text.includes(s.text.slice(0, 48)))).flatMap(s => s.rules))];
            const rules = own.length ? own : p.basis === 'sach' ? [...new Set(filled.rules)] : [];
            sentences.push({ text, basis: p.basis, kind: p.kind ?? 'claim', module: m.id, passage: p.id, rules, cites });
            recent.push(opener(text));
          }
        });
      }
      if (sentences.length) out.push({ module: m.id, role: m.role, title: this.fill(m.title)?.text ?? m.title, sentences, text: sentences.map(s => s.text).join(' ') });
    }
    return out;
  }

  private pick(m: ContentModule, p: Passage, idx: number, item: Record<string, Slot> | undefined, recent: string[]) {
    const pool = idx > 0 && p.followups?.length ? p.followups : p.variants;
    const n = pool.length, start = hash(`${this.seed}|${m.id}|${p.id}|${idx}`) % n;
    let fallback: Filled | null = null;
    for (let i = 0; i < n; i++) {
      const v = pool[(start + i) % n], f = this.fill(v, item);
      if (!f) continue;
      fallback ??= f;
      if (!recent.slice(-3).includes(opener(f.text))) return f;
    }
    return fallback;
  }
}

const CAPS: Record<string, number> = { generic: 2, base: 4, support: 3, qualifier_f: 4, qualifier_other: 2, env_pos: 2, env_neg: 2, timing: 3, work_style: 2 };
/** The palace a list's paragraph already names, so its items do not repeat it. */
const HOME: Record<string, (a: ArgumentGraph) => string | undefined> = {
  base: a => a.focus, support: a => a.focus, qualifier_f: a => a.focus, env_pos: a => a.spec.env?.palace, env_neg: a => a.spec.env?.palace,
};

/** Sentence split that never cuts inside quotes or parentheses. */
export function splitSentences(text: string): string[] {
  const out: string[] = []; let depth = 0, inQ = false, cur = '';
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]; cur += ch;
    if (ch === '(') depth++; else if (ch === ')') depth = Math.max(0, depth - 1);
    else if (ch === '“') inQ = true; else if (ch === '”') inQ = false;
    else if ((ch === '.' || ch === '?') && !depth && !inQ && (text[i + 1] === ' ' || i === text.length - 1)) { out.push(cur.trim()); cur = ''; }
  }
  if (cur.trim()) out.push(cur.trim());
  return out.filter(Boolean);
}
