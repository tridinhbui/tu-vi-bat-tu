// The owner's benchmark of domain judgements (plan THIEN-BAN-33 G4.4, owner decision Q3 2026-11-07): 30 cases in three groups of 10 and an
// independent holdout of 15, drawn deterministically from the corpus, each with the chart, the evidence the engine fired and its current
// draft conclusion, and empty fields for the owner: expected (lean, strength, dominant, reducers), forbidden conclusions, why.
//   A  a favourable structure with a light limit            (verdict thuận / có điều kiện + / nghiêng về + with a limit in the core palace)
//   B  strong conflict with a rescue or a chế hóa           (two sides, and a chế hóa or cứu giải relation in the core configuration)
//   C  missing condition, exception, over-reading risk      (a grave reading, a broken cách, or a single-star ground)
// The holdout is chosen from other charts before any weight is tuned and is not looked at while tuning (no overfitting).
//   node tools/interpret/make_gold_cases.ts   → src/interpret/test/fixtures/gold/{cases,holdout}.json + docs/gold/PHIEU-CHAM.md
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import type { ChartInput, Knowledge } from '../../src/interpret/types.ts';
import { infer } from '../../src/interpret/prose/chapter.ts';
import { analyses, type Analysis } from '../../src/interpret/reason/analysis.ts';

const K: Knowledge = JSON.parse(readFileSync('src/interpret/generated/knowledge.json', 'utf8'));
const corpus = (JSON.parse(gunzipSync(readFileSync('src/interpret/test/fixtures/corpus1000.json.gz')).toString()) as Array<{ facts: ChartInput; birth?: Record<string, unknown> }>);
type Case = { id: string; group: 'A' | 'B' | 'C' | 'holdout'; chart: number; birth?: Record<string, unknown>; domain: string; label: string; draft: Analysis['conclusion'] & { weigh?: string };
  evidence: { supporting: string[]; limiting: string[]; interactions: string[]; rescues: string[] };
  expected: { lean: string; strength: string; dominant: string; reducers: string }; forbidden: string[]; why: string };
const pick = (a: Analysis) => {
  const lim = a.limiting_evidence.length > 0, two = a.supporting_evidence.some(e => e.id.startsWith('rule:')) && a.limiting_evidence.some(e => e.id.startsWith('rule:'));
  if ((a.conclusion.type === 'thuan' || ((a.conclusion.type === 'co_dieu_kien' || a.conclusion.type === 'nghieng_ve') && a.conclusion.base === '+')) && lim) return 'A';
  if (two && (a.rescues.length || a.interactions.some(i => /chế|sợ|giải|kìm/u.test(i.text)))) return 'B';
  if (a.conclusion.severity === 'grave' || a.limiting_evidence.some(e => /bị phá/u.test(e.text)) || a.level <= 2) return 'C';
  return null;
};
const toCase = (i: number, a: Analysis, group: Case['group']): Case => ({ id: `${group}-${i}-${a.domain}`, group, chart: i, birth: corpus[i].birth, domain: a.domain, label: a.label, draft: a.conclusion,
  evidence: { supporting: a.supporting_evidence.map(e => `${e.id} | ${e.text}`), limiting: a.limiting_evidence.map(e => `${e.id} | ${e.text}`), interactions: a.interactions.map(e => `${e.text} (${e.cite ?? ''})`), rescues: a.rescues.map(e => `${e.text} (${e.cite ?? ''})`) },
  expected: { lean: '', strength: '', dominant: '', reducers: '' }, forbidden: [], why: '' });

const cases: Case[] = [], holdout: Case[] = [];
const want = { A: 10, B: 10, C: 10 } as Record<string, number>;
// charts 0-499 feed the 30 cases; 500-999 the holdout (disjoint charts), one domain per chart so no chart dominates
for (let i = 0; i < 500 && cases.length < 30; i++) {
  for (const a of analyses(corpus[i].facts, K, infer(corpus[i].facts, K).resolved, (corpus[i].facts.year as { age_tuoi_mu?: number } | undefined)?.age_tuoi_mu).domains) {
    const g = pick(a);
    if (g && want[g] > 0) { want[g]--; cases.push(toCase(i, a, g as Case['group'])); break; }
  }
}
for (let i = 997; i >= 500 && holdout.length < 15; i -= 31) {
  const ds = analyses(corpus[i].facts, K, infer(corpus[i].facts, K).resolved).domains.filter(d => d.conclusion.type !== 'khong_ket_luan');
  if (ds.length) holdout.push(toCase(i, ds[i % ds.length], 'holdout'));
}
mkdirSync('src/interpret/test/fixtures/gold', { recursive: true });
writeFileSync('src/interpret/test/fixtures/gold/cases.json', JSON.stringify(cases, null, 1));
writeFileSync('src/interpret/test/fixtures/gold/holdout.json', JSON.stringify(holdout, null, 1));
const md = ['# Phiếu chấm tình huống miền (G4.4)', '',
  'Mỗi tình huống: lá số (ngày giờ sinh trong corpus), miền đang xét, các chứng cứ bộ máy đã kích hoạt, và kết luận nháp hiện tại. Xin ghi vào `src/interpret/test/fixtures/gold/cases.json` (hoặc trả lời theo số thứ tự): `expected.lean` (thuận / khó / ngang), `expected.strength` (nhẹ / vừa / rõ), `expected.dominant` (yếu tố chi phối), `expected.reducers` (yếu tố làm giảm), `forbidden` (những kết luận không được phép), `why` (lý do).',
  '', 'Tập kiểm định độc lập (`holdout.json`, 15 tình huống từ các lá khác) xin chấm **trước** khi mình chỉnh trọng số; mình sẽ không mở nó trong lúc chỉnh. Bộ này đo tính nhất quán và chất lượng lập luận theo hệ quy tắc, không chứng minh khả năng dự đoán.', ''];
for (const [n, c] of [...cases, ...holdout].entries()) {
  md.push(`## ${n + 1}. ${c.group} · lá #${c.chart}${c.birth ? ` (${(c.birth as { day?: number }).day}/${(c.birth as { month?: number }).month}/${(c.birth as { year?: number }).year} ${(c.birth as { hour?: number }).hour}h, ${(c.birth as { gender?: string }).gender === 'male' ? 'nam' : 'nữ'})` : ''} · ${c.label}`, '',
    `Kết luận nháp: **${c.draft.type}${c.draft.base ? ` (${c.draft.base})` : ''}**, độ chắc ${c.draft.confidence}, tầm ${c.draft.scope}${c.draft.severity === 'grave' ? ', có câu nặng' : ''}`, '',
    '- Thuận:', ...c.evidence.supporting.slice(0, 8).map(x => `  - ${x}`), '- Khó:', ...c.evidence.limiting.slice(0, 8).map(x => `  - ${x}`),
    ...(c.evidence.interactions.length ? ['- Tương tác:', ...c.evidence.interactions.slice(0, 4).map(x => `  - ${x}`)] : []),
    ...(c.evidence.rescues.length ? ['- Cứu giải:', ...c.evidence.rescues.slice(0, 3).map(x => `  - ${x}`)] : []), '');
}
mkdirSync('docs/gold', { recursive: true });
writeFileSync('docs/gold/PHIEU-CHAM.md', md.join('\n'));
console.log(`${cases.length} cases (${['A', 'B', 'C'].map(g => `${g} ${cases.filter(c => c.group === g).length}`).join(', ')}), ${holdout.length} holdout`);
