// "Cả tổ hợp": one paragraph per domain palace that reads the palace's configuration as one structure (plan THIEN-BAN-33 G10.1, the
// owner's review 2026-11-07: "luận tổ hợp thay vì luận từng sao"; the five layers of a deep paragraph). Every sentence is built from
// reason/configuration.ts, nothing else:
//   1 bản chất   the core (own or borrowed chính tinh) and what the book says those stars are for this palace's matter (star_nature, cited)
//   2 cơ chế     the members that change the whole (Tứ Hóa, with its KL pp.195-197 meaning) and the ones that add strength
//   3 mâu thuẫn  the members that lessen it, with a chế hóa the book states between them
//   4 điều kiện  the nearest đại hạn (from the current one, before 80) that touches the members
//   5 giới hạn   the configuration's state and strength, said as the structure's direction, not a verdict on success
import type { ChartInput, Knowledge } from '../types.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import { configurationOf, strengthWord, type Configuration, type Member } from '../reason/configuration.ts';
import type { Resolved } from '../kg/resolve.ts';
import { finish, type Micro } from './micro.ts';

export interface WholeLib { title: string; l1: string[]; l1_core: string[]; l1_nature: string[]; l2: string[]; l2_bien: string[]; l2_tro: string[]; l2_none: string[]; l3: string[]; l4: string[]; l5: string[]; state: Record<string, string> }
const joinVi = (xs: string[]) => xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_]+)\}/g, (m, k) => v[k] ?? m);
const words = (t: string) => t.split(/\s+/).length;
const NOTE = 'Lời tổng hợp về cả tổ hợp của cung (reason/configuration.ts): sao chủ, sao đổi tính chất, trợ lực, phần cản và chặng kích hoạt, theo thứ tự cố định; quy ước có nhãn, không phải lời sách.';

export function wholeParagraph(chart: ChartInput, k: Knowledge, P: string, resolved: Resolved[], m: Micro, L: WholeLib): ProseParagraph | null {
  const c: Configuration = configurationOf(chart, k, P, resolved);
  if (c.state === 'chua_du' || !c.core.length) return null;
  const say = (xs: ProseSentence[], text: string, step: string, basis: SentenceTrace['basis'], cites: string[] = []) => {
    const t = finish(text);
    if (words(t) > 35) return false;
    m.said(t);
    xs.push({ text: t, trace: { move: 'VALUE', concepts: [], rules: [], cites, basis, step, part: 2, note: NOTE } as SentenceTrace });
    return true;
  };
  const xs: ProseSentence[] = [];
  const key = `whole|${P}`;
  // 1 bản chất
  const borrowed = c.core.some(x => x.borrowed);
  const dig = c.core[0].dignity ? ` (${c.core[0].dignity})` : '';
  const core = borrowed ? `vô chính diệu, mượn ${joinVi(c.core.map(x => x.name))}${dig} từ cung ${c.core[0].palace}` : `có ${joinVi(c.core.map(x => x.name))}${dig} làm chủ`;
  const nat = c.questions.find(q => q.q.startsWith('Sao chủ'));
  const natures = nat?.known ? nat.a.split('; ').map(x => x.replace(/\s*\(KL p\.\d+\)$/, '')) : [];
  const natCites = nat?.known ? [...nat.a.matchAll(/KL p\.(\d+)/g)].map(x => `KL p.${x[1]}`) : [];
  // one sentence when it fits in 35 words; else the core, then each nature on its own
  if (natures.length && !say(xs, fill(m.pick(`${key}|1`, L.l1), { pal: P, core, natures: joinVi(natures.slice(0, 2)) }), 'whole:1', 'sach', natCites)) {
    say(xs, fill(m.pick(`${key}|1c`, L.l1_core), { pal: P, core }), 'whole:1', 'tinh_toan');
    for (const [i, n] of natures.slice(0, 2).entries()) say(xs, fill(m.pick(`${key}|1n${i}`, L.l1_nature), { nature: n }), 'whole:1', 'sach', natCites[i] ? [natCites[i]] : natCites);
  } else if (!natures.length) say(xs, fill(m.pick(`${key}|1c`, L.l1_core), { pal: P, core }), 'whole:1', 'tinh_toan');
  // 2 cơ chế
  // a Hóa on a bright star or in the palace first, one on a hãm star last (it lifts only part of the fall)
  const bt = c.members.filter(x => x.role === 'bien_tinh').sort((a, b) => Number(a.dignity === 'hãm') - Number(b.dignity === 'hãm') || Number(b.where === 'self') - Number(a.where === 'self')), tl = c.members.filter(x => x.role === 'tro_luc');
  const btTxt = joinVi(bt.slice(0, 2).map(x => `${x.name} ở ${x.palace} (${x.does.replace(/^[^ ]+ là /, '')})`));
  const tlTxt = joinVi([...new Set(tl.map(x => x.name))].slice(0, 3));
  if (bt.length && !say(xs, fill(m.pick(`${key}|2`, L.l2), { bien: btTxt, tro: tlTxt || 'không sao nào' }), 'whole:2', 'tong_hop', ['KL pp.195-197'])) {
    say(xs, fill(m.pick(`${key}|2b`, L.l2_bien), { bien: btTxt }), 'whole:2', 'tong_hop', ['KL pp.195-197']);
    if (tl.length) say(xs, fill(m.pick(`${key}|2t`, L.l2_tro), { tro: tlTxt }), 'whole:2', 'tong_hop');
  }
  else if (tl.length) say(xs, fill(m.pick(`${key}|2n`, L.l2_none), { tro: tlTxt }), 'whole:2', 'tong_hop');
  // 3 mâu thuẫn
  const tr = c.members.filter(x => x.role === 'tru' || x.role === 'pha');
  if (tr.length) {
    const named = (x: Member) => `${x.name}${x.palace !== P ? ` (${x.palace})` : ''}`;
    // a chế hóa by which a lessening member weighs on a helping one (never a rescue: "giải", "cứu" relations are not the lessening side)
    const good = c.members.filter(x => x.role === 'nen' || x.role === 'bien_tinh' || x.role === 'tro_luc').map(x => x.name);
    const che = c.relations.find(r => r.kind === 'che' && tr.some(x => r.from.startsWith(`${x.name}@`)) && r.to !== `*@${P}`
      && r.to.split('@')[0].split('|').some(n => good.some(g => g.startsWith(n))) && !/giải|cứu|kìm|bớt/u.test(r.note));
    const why = che ? `; riêng ${che.from.split('@')[0]} chế ${che.to.split('@')[0].split('|').join(', ')}: ${che.note.includes(': ') ? che.note.split(': ').at(-1) : che.note}` : '';
    if (!say(xs, fill(m.pick(`${key}|3`, L.l3), { tru: joinVi(tr.slice(0, 3).map(named)), che: why }), 'whole:3', 'tong_hop', che?.cite ? [che.cite] : []))
      say(xs, fill(m.pick(`${key}|3`, L.l3), { tru: joinVi(tr.slice(0, 3).map(named)), che: '' }), 'whole:3', 'tong_hop');
  }
  // 4 điều kiện
  const age = (chart.year as { age_tuoi_mu?: number } | undefined)?.age_tuoi_mu ?? 0;
  const a = c.activation.find(x => x.age_to >= age && x.age_from < 80 && x.members.length);
  if (a) say(xs, fill(m.pick(`${key}|4`, L.l4), { age: `${a.age_from}–${a.age_to}`, what: a.what.split(', ').slice(0, 2).join(' và ').replace(/ của hạn vào /g, ' vào ') }), 'whole:4', 'tinh_toan');
  // 5 giới hạn
  say(xs, fill(m.pick(`${key}|5`, L.l5), { state: L.state[c.state] ?? c.state, strength: strengthWord(c.strength) }), 'whole:5', 'tong_hop');
  if (xs.length < 3) return null;
  return { role: 'support', sentences: xs, text: xs.map(s => s.text).join(' '), part: 2, title: L.title } as ProseParagraph;
}
