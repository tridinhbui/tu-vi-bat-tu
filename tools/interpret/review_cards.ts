// Prose-card review (prose plan P2). Two commands:
//   node tools/interpret/review_cards.ts page            -> docs/review/prose-cards.html: a self-contained page listing every card with the
//                                                          rules that assert its concept; the reviewer marks approve / revise / reject
//                                                          with a note, then downloads prose-reviews.json (decisions stay in the browser
//                                                          until downloaded).
//   node tools/interpret/review_cards.ts apply <file>    -> writes the decisions back: approve -> status 'approved', revise -> 'in_review',
//                                                          reject -> 'retired'; the note and reviewer go to engine/data/kg/prose_reviews.json.
// Rebuild knowledge.json afterwards (node tools/interpret/build.ts).
import { mkdirSync, readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = join(import.meta.dirname, '..', '..'), P = join(ROOT, 'src', 'interpret', 'content', 'prose');
const read = (p: string) => JSON.parse(readFileSync(p, 'utf8'));
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function page() {
  const K = read(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'));
  const rc: Record<string, { asserts: Array<{ concept: string }>; src: string }> = K.kg.ruleConcepts;
  const reading = Object.fromEntries(K.rules.map((r: any) => [r.id, `${r.reading ?? ''} ${(r.cites ?? []).join('; ')}`.trim()]));
  const byConcept: Record<string, string[]> = {};
  for (const [rid, e] of Object.entries(rc)) for (const a of e.asserts) (byConcept[a.concept] ??= []).push(rid);
  const field = (label: string, xs?: string[]) => xs?.length ? `<dt>${label}</dt><dd><ol>${xs.map(x => `<li>${esc(x)}</li>`).join('')}</ol></dd>` : '';
  const cards = K.prose.concepts.map((c: any) => {
    const rules = (byConcept[c.id] ?? []).slice(0, 8).map(r => `<li><code>${r}</code> ${esc(reading[r] ?? '')}</li>`).join('');
    return `<section class="card" data-id="${c.id}"><header><h2>${c.id}</h2><span class="np">${esc(c.np)}</span><span class="st">${c.status}</span></header>
<dl>${field('thường …', c.pred)}${field('câu hành vi', c.behave)}${field('dễ … (mặt trái)', c.turn)}${field('khi bị làm mềm', c.soft)}${field('điều đáng quý là …', c.value)}${field('khi biết …', c.mature)}</dl>
<details><summary>${(byConcept[c.id] ?? []).length} rule nói về concept này</summary><ul>${rules}</ul></details>
<div class="act"><label><input type="radio" name="${c.id}" value="approve"> Duyệt</label><label><input type="radio" name="${c.id}" value="revise"> Cần sửa</label><label><input type="radio" name="${c.id}" value="reject"> Bỏ</label>
<textarea placeholder="Ghi chú cho người biên tập"></textarea></div></section>`;
  }).join('\n');
  const html = `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Duyệt thẻ văn Mệnh</title>
<style>:root{--bg:#faf8f4;--fg:#222;--mut:#666;--line:#ddd;--acc:#8a5a00}@media (prefers-color-scheme:dark){:root{--bg:#1b1a18;--fg:#eee;--mut:#aaa;--line:#444;--acc:#e0a840}}
body{background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,sans-serif;max-width:900px;margin:0 auto;padding:16px}h1{font-size:22px}.card{border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:14px 0}
header{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}h2{font-size:16px;margin:0;font-family:ui-monospace,monospace}.np{color:var(--mut)}.st{margin-left:auto;font-size:12px;color:var(--acc)}
dt{font-weight:600;margin-top:8px}dd{margin:0}ol{margin:4px 0;padding-left:22px}details{color:var(--mut);font-size:13px;margin-top:8px}.act{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;align-items:center}
textarea{flex:1 1 100%;min-height:40px;background:transparent;color:var(--fg);border:1px solid var(--line);border-radius:6px}button{font:inherit;padding:6px 14px}#bar{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap}</style></head><body>
<h1>Duyệt thẻ văn cho chương Mệnh</h1><p>Mỗi thẻ chỉ quyết định <em>cách nói</em> một ý; ý ấy chỉ xuất hiện khi một rule đã kiểm và đang kích hoạt khẳng định nó. Đánh giá: câu có đúng nghĩa của các rule bên dưới không, có nói quá không, có tự nhiên không.</p>
<div id="bar"><input id="who" placeholder="Tên người duyệt"><button id="dl">Tải prose-reviews.json</button><span id="n"></span></div>
${cards}
<script>
const K='prose-reviews';let S={};try{S=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(S))}catch(e){};document.getElementById('n').textContent=Object.keys(S).length+' thẻ đã đánh giá'};
document.querySelectorAll('.card').forEach(c=>{const id=c.dataset.id,t=c.querySelector('textarea');if(S[id]){const r=c.querySelector('input[value="'+S[id].decision+'"]');if(r)r.checked=true;t.value=S[id].note||''}
c.querySelectorAll('input[type=radio]').forEach(r=>r.onchange=()=>{S[id]={...(S[id]||{}),decision:r.value};save()});t.oninput=()=>{S[id]={...(S[id]||{decision:'revise'}),note:t.value};save()}});
document.getElementById('dl').onclick=()=>{const who=document.getElementById('who').value||'?',at=new Date().toISOString();
const out=Object.entries(S).map(([id,v])=>({id,decision:v.decision,note:v.note||'',by:who,at}));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out,null,1)],{type:'application/json'}));a.download='prose-reviews.json';a.click()};save();
</script></body></html>`;
  mkdirSync(join(ROOT, 'docs', 'review'), { recursive: true });
  writeFileSync(join(ROOT, 'docs', 'review', 'prose-cards.html'), html);
  console.log(`docs/review/prose-cards.html: ${K.prose.concepts.length} cards`);
}

function apply(file: string) {
  const decisions: Array<{ id: string; decision: 'approve' | 'revise' | 'reject'; note: string; by: string; at: string }> = read(file);
  const to = { approve: 'approved', revise: 'in_review', reject: 'retired' } as const;
  const by = new Map(decisions.map(d => [d.id, d]));
  let n = 0;
  for (const f of readdirSync(P).filter(f => /^concepts_.*\.json$/.test(f))) {
    const doc = read(join(P, f));
    for (const c of doc.cards) { const d = by.get(c.id); if (d) { c.status = to[d.decision]; n++; } }
    writeFileSync(join(P, f), JSON.stringify(doc, null, 1) + '\n');
  }
  const logPath = join(ROOT, 'engine', 'data', 'kg', 'prose_reviews.json');
  const log = existsSync(logPath) ? read(logPath) : { note: 'Reviewer decisions on prose cards (tools/interpret/review_cards.ts apply).', reviews: [] };
  log.reviews.push(...decisions);
  writeFileSync(logPath, JSON.stringify(log, null, 1) + '\n');
  console.log(`${n} card(s) updated from ${decisions.length} decision(s)`);
}

const [cmd, arg] = process.argv.slice(2);
if (cmd === 'page') page(); else if (cmd === 'apply' && arg) apply(arg); else console.log('usage: review_cards.ts page | apply <prose-reviews.json>');
