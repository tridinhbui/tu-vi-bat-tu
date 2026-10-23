// "Đọc sâu" (plan DEEP-TUVI, 2026-10-22): the deep reading of Quan Lộc, Tài Bạch and Phu Thê, voiced from reason/depth.ts. One paragraph per
// section, under its own title, folded on the page under the chapter's short reading (report.js). What each sentence is:
//   deep:reading   a verified reading not yet told in the report (basis sach, its rule and page), or — when an earlier paragraph told it — a
//                  short back-reference (he_thong) so that the mechanism that follows has something to explain;
//   mechanism      the book's statement of what the star the reading stands on is (basis sach, cite only: KL page, no rule);
//   trigger        where the reading's elements stand when one is outside the palace (tinh_toan, computed from the trigger atoms);
//   tame / link    an interaction the chart has, as the book states it (sach) or as computed (tinh_toan);
//   cond           the domain ledger's verdicts gathered with the supports and limits they stand on (he_thong, no new claim);
//   minh_hoa       one illustration line tied to the claim right before it (owner's policy 2026-10-22; prose/checked.ts drops it with its claim).
// Each paragraph adds what the short reading did not say; a section with nothing new is left out. No timing and no event in Phu Thê.
import type { ChartInput, Knowledge } from '../types.ts';
import { depthConfig, domainDepth, type DepthReading, type DepthUnit, type UntoldReason } from '../reason/depth.ts';
import type { Writer } from './narrative.ts';
import type { ProseParagraph, ProseSentence, SentenceTrace } from './realize.ts';
import type { LuanShared } from './luan.ts';

export interface DepthLib {
  status: string; titles: Record<string, string>; claim: string[]; reduced: string[]; back: string[]; back_far: string[]; back_mech: string[]; mech_reading: string[]; mech_self: string[]; mech_vcd: string[]; mech_vcd_more: string[];
  mech_hoa: string[]; mech_limit: string[]; trigger: string[]; tame: string[]; link_hoa: string[]; hoa_meaning: string[]; link_shared: string[]; relation_facts: string[];
  ky_opp: string[]; condition_both: string[]; condition_sup: string[]; condition_lim: string[]; condition_pair: string[]; where: Record<string, string>;
}
export interface MinhHoaLib { status: string; concepts: Record<string, string[]> }

const fill = (t: string, v: Record<string, string>) => t.replace(/\{([A-Za-z_0-9]+)\}/g, (_, key) => { if (v[key] === undefined) throw new Error(`slot {${key}} unfilled in: ${t}`); return v[key]; });
const joinVi = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];
const cap = (s: string) => s.charAt(0).toLocaleUpperCase('vi') + s.slice(1);
const HOA_SHORT: Record<string, string> = { 'Hóa Lộc': 'Lộc', 'Hóa Quyền': 'Quyền', 'Hóa Khoa': 'Khoa', 'Hóa Kỵ': 'Kỵ' };

/** The deep paragraphs of one chapter (empty for a chapter without a deep reading). `said`: every sentence the report told before. */
export function deepParagraphs(chart: ChartInput, k: Knowledge, id: string, sh: LuanShared, W: Writer, said: ProseSentence[]): ProseParagraph[] {
  const D = k.prose?.depth;
  if (!depthConfig(k, id) || !D) return [];
  for (const r of k.kg?.starNature?.relations ?? []) REL_OF.set(r.id, r);
  const plan = domainDepth(chart, k, id, { resolved: sh.resolved, ledger: sh.ledger, said: sh.natureSaid, borrowed: sh.borrowed });
  const P = plan.palace;
  const untold = (sh.untold.get(id) ?? sh.untold.set(id, []).get(id)!);
  untold.push(...plan.untold);
  const note = (ruleId: string, reason: UntoldReason) => { if (!untold.some(u => u.ruleId === ruleId)) untold.push({ ruleId, reason }); };
  /** the sentence of the report that already voices this concept on this palace (a reading of another rule): the new rule corroborates it */
  const made: ProseSentence[] = [];
  // only a sentence of this chapter (the palace's own reading of the same thing): another chapter's corroboration line is not this palace's reading
  const own = new Set(sh.saidAll);
  const voicing = (concept: string, palace: string) => [...said.filter(s => !own.has(s)), ...made].reverse().find(s => s.trace.basis === 'sach' && (s.trace.keys ?? []).some(x => x === `${concept}@${palace}` || x.startsWith(`${concept}@${palace}|`)));
  const MH = k.prose?.minhHoa?.concepts ?? {};
  const DOM = (facet: string) => facet.startsWith('career.') && !facet.endsWith('.timing') ? 'cong_danh' : facet.startsWith('finance.') ? 'tai_loc'
    : facet === 'relationships.marriage' ? 'hon_nhan' : facet.startsWith('wellbeing.') ? 'suc_khoe' : null;
  const tied = (d: string) => sh.ledger.domains.some(v => v.id.split('.')[0] === d && !['thuan', 'chua_du', 'khong_ket_luan'].includes(v.verdict));
  const unexplained = (concept: string) => {
    const c = W.concept(concept), d = c && DOM(c.facet);
    if (!c || !d || c.pol === '~' || tied(d)) return false;
    // a limit against a domain the ledger concluded thuận (the report says so in the domain's own chapter, whatever the order of chapters)
    if (c.pol === '-' && sh.ledger.domains.some(v => v.id.split('.')[0] === d && v.verdict === 'thuan')) return true;
    return [...said, ...made].some(s0 => s0.trace.basis === 'sach' && s0.trace.concepts.some(y => { const cy = W.concept(y); return !!cy && DOM(cy.facet) === d && cy.pol !== '~' && cy.pol !== c.pol; }));
  };
  const toldRules = new Set(said.filter(s => s.trace.basis === 'sach').flatMap(s => s.trace.rules));
  const toldText = new Set(said.map(s => s.text));
  const out: ProseParagraph[] = [];
  const carrier = (h: string) => chart.tu_hoa[h]?.star ?? '';
  const where = (w: string | undefined, from: string) => fill(D.where[w ?? 'elsewhere'] ?? D.where.elsewhere, { from });
  const elName = (e: { name: string; palace: string }) => e.name.includes('|') ? `${e.name.split('|')[0]} hóa ${HOA_SHORT[e.name.split('|')[1]]}`
    : e.name.startsWith('Hóa ') ? `${carrier(e.name)} hóa ${HOA_SHORT[e.name]}` : e.name;
  /** the reading's elements by palace ("Thái Dương hóa Quyền ở cung Tài Bạch"); a star whose Hóa is named is not named twice */
  const named = (xs: Array<{ name: string; palace: string }>) => {
    const hoaStars = new Set(xs.filter(a => a.name.startsWith('Hóa ')).map(a => `${carrier(a.name)}@${a.palace}`));
    return xs.filter(a => a.name.startsWith('Hóa ') || !hoaStars.has(`${a.name}@${a.palace}`));
  };
  const ground = (x: DepthReading, onlyHere = false) => {
    const by = new Map<string, string[]>();
    for (const a of named(x.atoms.filter(a => !onlyHere || a.palace === x.palace))) { const n = elName(a); const xs = by.get(a.palace) ?? by.set(a.palace, []).get(a.palace)!; if (!xs.includes(n)) xs.push(n); }
    // a long ground (more than four names) keeps the palace's own elements and names the others only by the palace they come from
    const total = [...by.values()].reduce((n, ns) => n + ns.length, 0);
    const parts = [...by].sort((a, b) => Number(b[0] === x.palace) - Number(a[0] === x.palace)).map(([p, ns]) => {
      const vcd = ns.includes('vô chính diệu'), rest = ns.filter(n => n !== 'vô chính diệu');
      if (vcd) return rest.length ? `cung ${p} vô chính diệu có ${joinVi(rest)}` : `cung ${p} vô chính diệu`;
      if (total > 4 && p !== x.palace && rest.length > 1) return `các sao ở cung ${p}`;
      return `${joinVi(rest)} ở cung ${p}`;
    });
    return parts.length ? joinVi(parts) : `cung ${x.palace}`;
  };
  // the elements of a trigger, grouped by the palace they stand in ("Văn Khúc hóa Khoa và Thái Dương hóa Quyền ở cung Tài Bạch hội chiếu về")
  const trigEls = (u: DepthUnit) => {
    const by = new Map<string, { names: string[]; where?: string }>();
    for (const e of named(u.elements!)) { const g = by.get(e.palace) ?? by.set(e.palace, { names: [], where: (e as { where?: string }).where }).get(e.palace)!; const n = elName(e); if (!g.names.includes(n)) g.names.push(n); }
    return joinVi([...by].map(([p, g]) => `${joinVi(g.names)} ở cung ${p}${g.where === 'opp' ? ' xung chiếu sang' : g.where === 'trine' ? ' hội chiếu về' : ''}`));
  };
  const backed = new Set<string>(), consumed = new Set<DepthUnit>(), alone = new Set<DepthUnit>();
  // a trigger names where a reading's elements stand; the same elements are named once per chapter (no sentence repeats another's ground)
  const trigSeen = new Set<string>();
  const tsig = (u: DepthUnit) => named(u.elements!).map(e => `${e.name}@${e.palace}`).sort().join('|');
  const trigNew = (u?: DepthUnit) => !!u && !trigSeen.has(tsig(u));
  const S = (text: string, trace: Partial<SentenceTrace> & { move: SentenceTrace['move']; step: string }) => W.sentence(text, trace);
  for (const sec of plan.sections) {
    const xs: ProseSentence[] = [];
    const ordered = orderUnits(sec.units);
    let anchored = false, vcdN = 0;
    for (const u of ordered) {
      const key = `deep|${id}|${sec.id}|${xs.length}`;
      if (u.kind === 'reading') {
        const x = u.reading!;
        const told = toldRules.has(x.ruleId);
        const mech = ordered.find(v => v.kind === 'mechanism' && v.reading === x), trig = ordered.find(v => v.kind === 'trigger' && v.reading === x);
        const r = W.read(x.ruleId);
        if (told) {
          // a reading the report already told is only recalled when a mechanism or a trigger follows to explain it, once per concept
          // a borrowed reading's rule told once covers all it reads (its words name the borrowed stars); nothing to recall
          if (backed.has(x.concept) || x.borrowed) { if (trig) consumed.add(trig); if (mech) alone.add(mech); continue; }
          if (!mech && !trigNew(trig)) { if (trig) consumed.add(trig); continue; }
          backed.add(x.concept);
          // a recall names the reading by its short form: the full noun phrase was said where it was told
          const np = W.concept(x.concept)?.short ?? W.np(x.concept);
          if (trig && !trigNew(trig)) { consumed.add(trig); }
          if (trigNew(trig) && !x.atoms.some(a => a.palace === x.palace)) {
            consumed.add(trig!); trigSeen.add(tsig(trig!));
            xs.push(S(fill(W.pick(`${key}|bf`, D.back_far), { np, pal: P, els: trigEls(trig!) }), { move: 'VIA', step: `trigger:${x.ruleId}`, basis: 'tinh_toan', rules: [x.ruleId], cites: x.cites, concepts: [] }));
            anchored = true;
          } else if (mech && (!trig || consumed.has(trig)) && D.back_mech?.length) {
            // the recall and its reason in one sentence: the reading told above, and what the star it stands on is (no words spent on a bare recall)
            consumed.add(mech);
            xs.push(S(fill(W.pick(`${key}|bm`, D.back_mech), { Np: cap(np), np, ground: x.atoms.some(a => a.name === mech.star && a.palace === x.palace) ? `${mech.star} ở cung ${x.palace}` : ground(x, true), star: mech.star!, text: mech.nature!.text }),
              { move: 'ELABORATE', step: `mechanism:${mech.nature!.id}`, basis: 'sach', cites: [`${mech.nature!.book ?? "KL"} p.${mech.nature!.page}`], concepts: [] }));
            anchored = true;
          } else if (trigNew(trig) && (D as DepthLib & { back_with?: string[] }).back_with?.length) {
            // the recall, then the elements outside the palace it also needs (two short sentences of one frame)
            consumed.add(trig!); trigSeen.add(tsig(trig!));
            const [t1, t2] = fill(W.pick(`${key}|bw`, (D as DepthLib & { back_with: string[] }).back_with), { Np: cap(np), np, ground: ground(x, true), els: trigEls(trig!) }).split('. ');
            xs.push(S(t1, { move: 'VIA', step: `trigger:${x.ruleId}`, basis: 'tinh_toan', rules: [x.ruleId], cites: x.cites, concepts: [] }));
            if (t2) xs.push(S(t2, { move: 'VIA', step: `trigger:${x.ruleId}:far`, basis: 'tinh_toan', rules: [x.ruleId], cites: x.cites, concepts: [] }));
            anchored = true;
          }
          continue;
        }
        // the same reading (concept and palace) already told by another rule: this rule corroborates that sentence, it is not told twice
        // a reading against the side the report already told of a life domain (career, money, marriage, health) when no conditional verdict of
        // that domain ties the two sides: it would be a contradiction left unexplained — not told, and the trace says why
        if (unexplained(x.concept)) { note(x.ruleId, 'domain_unexplained'); if (mech) alone.add(mech); if (trig) consumed.add(trig); continue; }
        const same = voicing(x.concept, x.palace);
        if (same) {
          (same.trace.also ??= []).includes(x.ruleId) || same.trace.also!.push(x.ruleId);
          sh.voiced.add(x.ruleId); toldRules.add(x.ruleId);
          if (mech) alone.add(mech); if (trig) consumed.add(trig);
          continue;
        }
        const claim = r.claim ?? (W.pred(x.concept, x.status !== 'holds', key) ? `${W.S(x.concept)} ${W.pred(x.concept, x.status !== 'holds', key)}` : null);
        if (x.borrowed) {
          // a borrowed chính tinh (TT p.18): named as borrowed, from where it stands; lower confidence, said in the words and in the note
          if (trig) consumed.add(trig);
          const BT = (D as DepthLib & { borrow_claim?: string[] }).borrow_claim;
          if (!claim || !BT?.length) { if (mech) alone.add(mech); continue; }
          const stars = x.borrowed.stars.filter(st => x.atoms.some(a => a.name === st));
          const rest = x.atoms.filter(a => !(stars.includes(a.name) && a.palace === x.borrowed!.from));
          const extra = rest.length ? `, cùng ${ground({ ...x, atoms: rest })}` : '';
          sh.voiced.add(x.ruleId); toldRules.add(x.ruleId);
          const step = `deep:borrowed:${x.ruleId}`;
          xs.push(S(fill(W.pick(`${key}|bc`, BT), { pal: P, stars: joinVi(stars.length ? stars : x.borrowed.stars), from: x.borrowed.from, extra, claim }),
            { move: 'ANCHOR', step, concepts: [x.concept], rules: [x.ruleId], cites: x.cites, keys: [`${x.concept}@${x.palace}|${x.ruleId}`],
              note: 'Cung vô chính diệu mượn chính tinh của cung xung chiếu làm chủ (Toàn Thư tr.18); nhận định đứng trên sao mượn nhẹ hơn nhận định của sao tọa thủ.' }));
          made.push(xs[xs.length - 1]);
          anchored = true;
          continue;
        }
        if (!claim) { note(x.ruleId, 'no_text'); if (mech) alone.add(mech); if (trig) consumed.add(trig); continue; }
        // the claim's ground already names every element it stands on, wherever it stands: no separate trigger sentence
        if (trig) { consumed.add(trig); trigSeen.add(tsig(trig)); }
        sh.voiced.add(x.ruleId); toldRules.add(x.ruleId);
        const step = `deep:reading:${x.ruleId}`;
        const g = ground(x);
        const DX = D as DepthLib & { claim_against?: string[]; claim_reduced?: string[] };
        // the other side of a reading the report already told (its opposite concept on the same palace): told as the other side, never as if
        // nothing had been said; a reading whose book reducer the report already told is told as reduced
        const opp = W.concept(x.concept)?.opp;
        const against = !!opp && !!voicing(opp, x.palace) && !!DX.claim_against?.length;
        const reducedTold = !!x.reducedBy && toldRules.has(x.reducedBy) && !!DX.claim_reduced?.length;
        const frame = against ? DX.claim_against! : reducedTold ? DX.claim_reduced! : D.claim;
        xs.push(S(fill(W.pick(`${key}|claim`, frame), { ground: g, Ground: cap(g), claim }), { move: against || reducedTold ? 'TURN' : 'ANCHOR', step, concepts: [x.concept], rules: [x.ruleId], cites: x.cites,
          keys: [`${x.concept}@${x.palace}|${x.ruleId}`], ...(reducedTold ? { soft: true } : {}) }));
        made.push(xs[xs.length - 1]);
        anchored = true;
        if (x.reducedBy) {
          const rc = W.read(x.reducedBy).claim;
          const rr = W.rule(x.reducedBy);
          if (rc && rr && !toldRules.has(x.reducedBy)) xs.push(S(fill(W.pick(`${key}|red`, D.reduced), { claim: rc }), { move: 'TURN', step: `deep:reducer:${x.reducedBy}`, rules: [x.reducedBy], cites: rr.cites, concepts: [] }));
        }
        // the minh họa of this claim (only for a claim told here and told plainly, so that the line sits next to it)
        const mh = MH[x.concept];
        if (mh?.length && !against && !x.reducedBy && !sh.minhSaid.has(x.concept)) {
          sh.minhSaid.add(x.concept);
          const t = W.pick(`${key}|mh`, mh).replace(/\{S\}/g, W.S(x.concept));
          xs.push(S(t, { move: 'ELABORATE', step: `minh_hoa:${x.concept}`, basis: 'minh_hoa', tied: step, concepts: [], rules: [] }));
        }
      } else if (u.kind === 'mechanism') {
        // the mechanism of a reading that was not told (or folded into another of the same matter) has nothing to explain
        if (alone.has(u) || consumed.has(u)) continue;
        const n = u.nature!, cite = [`${n.book ?? "KL"} p.${n.page}`];
        let text: string;
        if (u.reading && !alone.has(u)) text = fill(W.pick(`${key}|mr`, D.mech_reading), { star: u.star!, text: n.text });
        else if (u.elements?.length && u.star?.startsWith('Hóa ')) text = fill(W.pick(`${key}|mh`, D.mech_hoa), { carrier: u.elements[0].name.split('|')[0], short: HOA_SHORT[u.star], hoa: u.star, pal: P, text: n.text });
        else if (u.where === 'trine') text = fill(W.pick(`${key}|mv`, vcdN++ ? D.mech_vcd_more : D.mech_vcd), { pal: P, star: u.star!, from: u.palace!, text: n.text });
        else if (n.pol === '-') text = fill(W.pick(`${key}|ml`, D.mech_limit), { star: u.star!, pal: P, text: n.text });
        else text = fill(W.pick(`${key}|ms`, D.mech_self), { star: u.star!, pal: P, text: n.text });
        anchored = true;
        xs.push(S(text, { move: 'ELABORATE', step: `mechanism:${n.id}`, basis: 'sach', cites: cite, concepts: [] }));
      } else if (u.kind === 'trigger') {
        if (consumed.has(u) || !trigNew(u)) continue;
        trigSeen.add(tsig(u));
        xs.push(S(fill(W.pick(`${key}|tr`, D.trigger), { pal: P, els: trigEls(u) }), { move: 'VIA', step: `trigger:${u.reading!.ruleId}`, basis: 'tinh_toan', rules: [u.reading!.ruleId], cites: u.reading!.cites, concepts: [] }));
        anchored = true;
      } else if (u.kind === 'tame') {
        const n = u.nature!;
        xs.push(S(fill(W.pick(`${key}|tm`, D.tame), { holder: u.star!, where: where(u.where, u.palace!), text: n.text, tamed: joinVi(u.tamed!.split('|')), pal: P }),
          { move: 'TURN', step: `tame:${n.id}`, basis: 'sach', cites: [`${n.book ?? "KL"} p.${n.page}`], concepts: [] }));
        anchored = true;
      } else if (u.kind === 'link') {
        if (u.link === 'than' || u.link === 'relation') {
          const r = u.relation!;
          const facts = relationFacts(chart, r.id, sh);
          // a relation the book states for every chart is told with this chart's side in the same sentence (a bare general line repeats from chart to chart)
          const rel = (D as DepthLib & { relation_with?: Record<string, string[]> }).relation_with?.[r.id];
          if (facts && rel?.length) xs.push(S(fill(W.pick(`${key}|rw`, rel), { facts }), { move: 'VIA', step: `link:${r.id}`, basis: 'sach', cites: [`${r.book ?? "KL"} p.${r.page}`], concepts: [] }));
          else {
            xs.push(S(cap(r.text), { move: 'VIA', step: `link:${r.id}`, basis: 'sach', cites: [`${r.book ?? "KL"} p.${r.page}`], concepts: [] }));
            if (facts) xs.push(S(fill(W.pick(`${key}|rf`, D.relation_facts), { facts }), { move: 'VIA', step: `link:${r.id}:facts`, basis: 'tinh_toan', concepts: [] }));
          }
          anchored = true;
        } else if (u.link === 'hoa') {
          const list = joinVi(groupHoa(u.elements!.map(e => ({ text: elName(e), palace: e.palace }))));
          xs.push(S(fill(W.pick(`${key}|lh`, D.link_hoa), { list }), { move: 'VIA', step: 'link:tu_hoa', basis: 'tinh_toan', concepts: [] }));
          const M = k.reference?.tuHoa?.meaning ?? {};
          const present = [...new Set(u.elements!.map(e => e.name.split('|')[1]))].filter(h => M[h] && h !== 'Hóa Kỵ');
          if (present.length) xs.push(S(fill(W.pick(`${key}|hm`, D.hoa_meaning), { list: joinVi(present.map(h => `${HOA_SHORT[h]} là ${M[h].replace(/\s*\(.*\)$/, '')}`)) }),
            { move: 'ELABORATE', step: 'mechanism:tu_hoa', basis: 'sach', cites: [k.reference?.tuHoa?.cite ?? 'KL pp.195-197'], concepts: [] }));
          anchored = true;
        } else if (u.link === 'shared_star') {
          const n = u.nature!;
          xs.push(S(fill(W.pick(`${key}|ls`, D.link_shared), { star: u.star!, where: u.palace === P ? `ở cung ${P}` : `ở cung ${u.palace}`, text: n.text }),
            { move: 'VIA', step: `link:${n.id}`, basis: 'sach', cites: [`${n.book ?? "KL"} p.${n.page}`], concepts: [] }));
          anchored = true;
        } else if (u.link === 'ky_opp') {
          const e = u.elements![0];
          xs.push(S(fill(W.pick(`${key}|ky`, D.ky_opp), { pal: P, star: e.name.split('|')[0], from: e.palace }), { move: 'TURN', step: 'link:ky_opp', basis: 'tinh_toan', confront: [], concepts: [] }));
          anchored = true;
        }
      } else if (u.kind === 'condition') {
        const cs = conditionSentences(W, k, D, u, key, P);
        xs.push(...cs);
      }
    }
    const fresh = xs.filter(s => !toldText.has(s.text));
    // a section that recalls only, or only conditions, adds nothing: left out
    if (!anchored || !fresh.some(s => s.trace.basis === 'sach' || s.trace.basis === 'tinh_toan')) continue;
    fresh.forEach(s => { s.trace.part = s.trace.step?.startsWith('cond:') ? 5 : s.trace.move === 'TURN' ? 4 : /^(trigger|link|tame)/.test(s.trace.step ?? '') ? 3 : 2; toldText.add(s.text); });
    out.push({ role: 'support', sentences: fresh, text: fresh.map(s => s.text).join(' '), deep: true, title: D.titles[sec.id] ?? sec.id, topic: `deep_${sec.id}`, part: fresh[0].trace.part });
  }
  return out;
}

/** a reading, then its trigger and mechanism; other units after the readings, in their order */
function orderUnits(us: DepthUnit[]): DepthUnit[] {
  const out: DepthUnit[] = [];
  for (const u of us.filter(x => x.kind === 'reading')) out.push(u, ...us.filter(v => v.reading === u.reading && v.kind === 'trigger'), ...us.filter(v => v.reading === u.reading && v.kind === 'mechanism'));
  out.push(...us.filter(u => u.kind !== 'reading' && !u.reading && u.kind !== 'condition'), ...us.filter(u => u.kind === 'condition'));
  return out;
}

/** "Cự Môn hóa Lộc ở Mệnh, Thái Dương hóa Quyền và Văn Khúc hóa Khoa ở Tài Bạch" */
function groupHoa(xs: Array<{ text: string; palace: string }>): string[] {
  const by = new Map<string, string[]>();
  for (const x of xs) (by.get(x.palace) ?? by.set(x.palace, []).get(x.palace)!).push(x.text);
  return [...by].map(([p, ts]) => `${joinVi(ts)} ở ${p}`);
}

/** the chart's side of a palace relation: what stands in the palaces the book names */
function relationFacts(chart: ChartInput, id: string, sh: LuanShared): string | null {
  const brief = (name: string) => {
    const p = chart.palaces.find(x => x.name === name)!;
    const ms = p.major_stars.map(s => p.major_dignity?.[s] ? `${s} (${p.major_dignity[s]})` : s);
    return ms.length ? `${name} có ${joinVi(ms)}` : `${name} không có chính tinh`;
  };
  if (id === 'tai.che_tai') {
    const v = sh.ledger.domains.find(d => d.id === 'cong_danh');
    return `${brief('Phúc Đức')}, ${brief('Quan Lộc')}` + (v && v.verdict !== 'chua_du' ? `; đường công danh đã được xét là ${LV[v.verdict === 'co_dieu_kien' ? `co_dieu_kien${v.base ?? ''}` : v.verdict] ?? v.verdict}` : '');
  }
  if (id === 'dien.ben') {
    const v = sh.ledger.domains.find(d => d.id === 'tai_loc.tich_luy');
    return `${brief('Tài Bạch')}` + (v && !['chua_du', 'khong_ket_luan'].includes(v.verdict) ? `, còn phần tích lũy, nhà cửa đã được xét là ${LV[v.verdict === 'co_dieu_kien' ? `co_dieu_kien${v.base ?? ''}` : v.verdict] ?? v.verdict}` : '');
  }
  // any other relation: the book's statement told with what stands, on this chart, in the palaces it names (its own palace when it names
  // none), and the ledger's verdict of the domain it ties to (Mệnh–Quan Lộc: công danh; Phu Thê–Phúc Đức: hôn nhân; Nô Bộc: kiếm tiền)
  const rel = (REL_OF.get(id));
  if (!rel || rel.when === "than") return null;
  const v = REL_VERDICT[id] ? sh.ledger.domains.find(d => d.id === REL_VERDICT[id]) : undefined;
  const verdict = v && !['chua_du', 'khong_ket_luan'].includes(v.verdict) ? `; ${v.label} đã được xét là ${LV[v.verdict === 'co_dieu_kien' ? `co_dieu_kien${v.base ?? ''}` : v.verdict] ?? v.verdict}` : '';
  return joinVi((rel.with ?? [rel.palace]).map(brief)) + verdict;
}
/** the relation of each id (set by deepParagraphs from the knowledge) and the ledger domain a relation ties to */
const REL_OF = new Map<string, { palace: string; with?: string[]; when?: string }>();
const REL_VERDICT: Record<string, string> = { 'menh.quan_di_tai': 'cong_danh', 'phuc.nu_menh_phu_phuc': 'hon_nhan', 'no.giau_ngheo_vi_ban': 'tai_loc.kiem' };
const LV: Record<string, string> = { thuan: 'thuận', 'co_dieu_kien+': 'thuận có điều kiện', 'co_dieu_kien-': 'vướng nhưng có lối gỡ', co_dieu_kien: 'tùy lúc', hai_chieu: 'hai chiều', tro_ngai: 'chỗ phải gắng sức', chua_phan_xu: 'còn hai mặt chưa phân xử được', hai_mat: 'có cả hai mặt', giam_nhe: 'vướng, có yếu tố giảm nhẹ' };

function conditionSentences(W: Writer, k: Knowledge, D: DepthLib, u: DepthUnit, key: string, P: string): ProseSentence[] {
  const G = k.prose!.luan!.ledger;
  const words = (v: NonNullable<DepthUnit['verdicts']>[number]) => { const vk = v.verdict === 'co_dieu_kien' ? `co_dieu_kien${v.base ?? ''}` : v.verdict; return G.verdict[vk] ? W.pick(`dv|${v.id}`, G.verdict[vk]) : ''; };
  const name = (e: { kind: string; star?: string; hoa?: string; dignity?: string }) => e.kind === 'tuan' ? 'Tuần' : e.kind === 'triet' ? 'Triệt' : e.kind === 'hoa_ky' ? 'Hóa Kỵ'
    : e.kind === 'ky_carrier' ? `${e.star} hóa Kỵ${(e as { borrowed?: boolean }).borrowed ? ' (mượn từ cung đối)' : ''}` : e.kind === 'major_ham' ? `${e.star} hãm${(e as { borrowed?: boolean }).borrowed ? ' (mượn từ cung đối)' : ''}` : e.kind === 'hoa_good' ? `${e.hoa}` : e.star ?? '';
  const tr = (v: NonNullable<DepthUnit['verdicts']>[number], step: string): Partial<SentenceTrace> & { move: SentenceTrace['move']; step: string } => {
    const items = [...v.pos, ...v.neg, ...v.timing, ...v.mixed];
    return { move: 'VALUE', step, basis: 'he_thong', concepts: [], rules: [...new Set(items.map(x => x.ruleId))].sort(), cites: [...new Set(items.flatMap(x => x.cites))].sort(),
      ledger: { domain: v.id, verdict: v.verdict, base: v.base } };
  };
  const vs = u.verdicts!, out: ProseSentence[] = [];
  const main = vs[0];
  const sup = [...new Set(main.supports.filter(s => s.palace === P).map(name))].filter(Boolean).slice(0, 3);
  const lim = [...new Set(main.limits.filter(s => s.palace === P && !(s.kind === 'hoa_ky' && main.limits.some(m => m.kind === 'ky_carrier'))).map(name))].filter(Boolean).slice(0, 3);
  const label = main.label;
  if (sup.length && lim.length) out.push(W.sentence(fill(W.pick(`${key}|cb`, D.condition_both), { label, supports: joinVi(sup), limits: joinVi(lim) }), tr(main, `cond:${main.id}:sides`)));
  else if (sup.length && main.verdict === 'thuan') out.push(W.sentence(fill(W.pick(`${key}|cs`, D.condition_sup), { label, supports: joinVi(sup) }), tr(main, `cond:${main.id}:sides`)));
  else if (lim.length) out.push(W.sentence(fill(W.pick(`${key}|cl`, D.condition_lim), { label, limits: joinVi(lim) }), tr(main, `cond:${main.id}:sides`)));
  // two domains side by side (công danh with kiếm tiền; the three parts of money): one sentence, the ledger's own words
  const pair = vs.slice(0, 2).filter(v => words(v));
  const w1 = pair[0] ? words(pair[0]) : '';
  let w2 = pair[1] ? words(pair[1]) : '';
  if (pair[1] && w2 === w1) { const vk = pair[1].verdict === 'co_dieu_kien' ? `co_dieu_kien${pair[1].base ?? ''}` : pair[1].verdict; w2 = (G.verdict[vk] ?? []).find(x => x !== w1) ?? w2; }
  if (pair.length === 2) out.push(W.sentence(fill(W.pick(`${key}|cp`, D.condition_pair), { label1: pair[0].label, verdict1: w1, label2: pair[1].label, verdict2: w2 }),
    { ...tr(pair[0], `cond:${pair[0].id}+${pair[1].id}`), rules: [...new Set([...tr(pair[0], '').rules!, ...tr(pair[1], '').rules!])].sort() }));
  return out;
}
