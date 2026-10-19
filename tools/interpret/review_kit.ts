// Human review kit for Mệnh reader prose (prose plan P4). Two self-contained pages and a scorer:
//   node tools/interpret/review_kit.ts pages          -> docs/review/prose-rating.html  (blind rating: 60 machine paragraphs + the
//                                                       human paragraphs of docs/review/human_paragraphs.json, shuffled, unlabelled)
//                                                    -> docs/review/prose-gold.html    (gold set: 50 charts, every sentence judged
//                                                       đúng / quá đà / sai / không chắc against the chart and its evidence)
//   node tools/interpret/review_kit.ts score <rating.json> <gold.json>
//                                                    -> docs/examples/prose-review-scores.md, against the plan §6 thresholds
// Pages keep a draft in the browser (localStorage) and hand the result back as a downloaded JSON file; nothing is sent anywhere.
import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
import { proseMenh, type ProseChapter } from '../../src/interpret/prose/menh.ts';
import { fnv } from '../../src/interpret/prose/micro.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const read = (p: string) => JSON.parse(readFileSync(p, 'utf8'));
const esc = (s: string) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const K: Knowledge = read(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'));
const corpus = () => JSON.parse(gunzipSync(readFileSync(join(ROOT, 'src', 'interpret', 'test', 'fixtures', 'corpus1000.json.gz'))).toString('utf8'));

/** Charts spread over paragraph schemas and Mệnh configurations: every k-th chart of the corpus sorted by (schema, stars, seed hash). */
function sample(n: number, salt: string): Array<{ c: any; o: ProseChapter }> {
  const all = corpus().map((c: any) => ({ c, o: proseMenh(c.facts, K, { allowDraft: true }) })).filter((x: any) => x.o.paragraphs.length);
  const key = (x: any) => `${x.o.schema}|${x.c.facts.palaces.find((p: any) => p.name === 'Mệnh').major_stars.join('+')}|${fnv(salt + JSON.stringify(x.c.birth)).toString(36)}`;
  all.sort((a: any, b: any) => key(a) < key(b) ? -1 : 1);
  const step = all.length / n;
  return Array.from({ length: n }, (_, i) => all[Math.floor(i * step)]);
}
const chartLine = (c: any) => {
  const m = c.facts.palaces.find((p: any) => p.name === 'Mệnh'), hoa = Object.entries(c.facts.tu_hoa).filter(([, v]: any) => v.branch === m.branch_index).map(([k]) => k);
  return `${c.birth.day}/${c.birth.month}/${c.birth.year} ${String(c.birth.hour).padStart(2, '0')}:${String(c.birth.minute).padStart(2, '0')} ${c.birth.gender === 'male' ? 'nam' : 'nữ'} · Mệnh ${m.stem} ${m.branch}: ${m.major_stars.map((s: string) => `${s}${m.major_dignity[s] ? ` (${m.major_dignity[s]})` : ''}`).join(', ') || 'vô chính diệu'}${hoa.length ? ' · ' + hoa.join(', ') : ''}${m.tuan ? ' · Tuần' : ''}${m.triet ? ' · Triệt' : ''} · phụ tinh: ${m.stars.filter((s: string) => !m.major_stars.includes(s)).join(', ')}`;
};

const STYLE = `:root{--bg:#faf8f4;--fg:#1f1d1a;--mut:#6b655c;--line:#ddd6ca;--acc:#8a5a00;--raise:#fffdf9}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1b1a18;--fg:#eee9e0;--mut:#a9a297;--line:#3d3a35;--acc:#e0a840;--raise:#24221f}}
body{background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:16px}h1{font-size:22px;margin:8px 0}
.card{background:var(--raise);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0}.txt{font:16px/1.75 Georgia,serif}
.mut{color:var(--mut);font-size:13px}.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:10px}label{cursor:pointer}
textarea{width:100%;min-height:36px;background:transparent;color:var(--fg);border:1px solid var(--line);border-radius:6px;font:inherit;box-sizing:border-box}
#bar{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap;z-index:2}
button,input{font:inherit}button{padding:6px 14px}.s{padding:6px 0;border-top:1px dashed var(--line)}.s:first-child{border-top:0}.why{font-size:13px;color:var(--mut);margin-top:4px}
code{font-size:12px}`;
const SCRIPT = (key: string, file: string) => `<script>
const K='${key}';let S={};try{S=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(S))}catch(e){};document.getElementById('n').textContent=Object.keys(S).length+' mục đã chấm'};
document.querySelectorAll('[data-k]').forEach(el=>{const k=el.dataset.k,v=S[k]||{};el.querySelectorAll('input[type=radio]').forEach(r=>{if(v[r.name.split('|')[1]]===r.value)r.checked=true;r.onchange=()=>{S[k]={...(S[k]||{}),[r.name.split('|')[1]]:r.value};save()}});
const t=el.querySelector('textarea');if(t){t.value=v.note||'';t.oninput=()=>{S[k]={...(S[k]||{}),note:t.value};save()}}});
document.getElementById('dl').onclick=()=>{const who=document.getElementById('who').value||'?';const out={by:who,at:new Date().toISOString(),items:S};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(out,null,1)],{type:'application/json'}));a.download='${file}';a.click()};save();
</script>`;
const page = (title: string, intro: string, body: string, key: string, file: string) => `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><style>${STYLE}</style></head><body>
<h1>${title}</h1>${intro}<div id="bar"><input id="who" placeholder="Tên người chấm"><button id="dl">Tải kết quả (${file})</button><span id="n" class="mut"></span></div>${body}${SCRIPT(key, file)}</body></html>`;

function pages() {
  // ---- blind rating ----
  const machine = sample(60, 'rating').map(({ c, o }, i) => ({ id: `M${String(i + 1).padStart(2, '0')}`, text: o.paragraphs[0].text, chart: chartLine(c) }));
  const human = (read(join(ROOT, 'docs', 'review', 'human_paragraphs.json')).paragraphs as Array<{ id: string; text: string; chart: string }>);
  const items = [...machine, ...human].map(x => ({ ...x, blind: 'P' + (fnv('blind' + x.id) % 100000).toString(36) })).sort((a, b) => a.blind < b.blind ? -1 : 1);
  const key = Object.fromEntries(items.map(x => [x.blind, x.id]));
  const radios = (k: string, field: string, opts: Array<[string, string]>) => opts.map(([v, l]) => `<label><input type="radio" name="${k}|${field}" value="${v}"> ${l}</label>`).join('');
  const rating = items.map((x, i) => `<div class="card" data-k="${x.blind}"><p class="mut">${i + 1}/${items.length} · ${esc(x.chart)}</p><p class="txt">${esc(x.text)}</p>
    <div class="row"><b>Độ tự nhiên</b>${radios(x.blind, 'score', [['1', '1 · rời rạc'], ['2', '2'], ['3', '3 · đọc được'], ['4', '4'], ['5', '5 · như người viết']])}</div>
    <div class="row"><b>Bạn đoán</b>${radios(x.blind, 'guess', [['human', 'người viết'], ['machine', 'máy ghép'], ['unsure', 'không chắc']])}</div><textarea placeholder="Câu nào gượng, lặp, hay nói quá?"></textarea></div>`).join('');
  mkdirSync(join(ROOT, 'docs', 'review'), { recursive: true });
  writeFileSync(join(ROOT, 'docs', 'review', 'prose-rating.html'), page('Chấm mù văn luận giải cung Mệnh',
    `<p>Mỗi đoạn dưới đây là luận giải cung Mệnh cho một lá số. Một số đoạn do người viết, số còn lại do bộ máy quy tắc ghép; thứ tự đã xáo và không ghi nguồn. Chấm độ tự nhiên 1–5 và đoán nguồn. Đừng đối chiếu sách ở đây: tính đúng sai được chấm ở trang bộ vàng.</p>${human.length < 15 ? `<p class="mut"><b>Lưu ý:</b> hiện mới có ${human.length} đoạn người viết; chỉ số “không nhận ra máy” cần ít nhất 15 (thêm vào docs/review/human_paragraphs.json).</p>` : ''}`,
    rating, 'prose-rating', 'prose-rating.json'));
  writeFileSync(join(ROOT, 'docs', 'review', 'prose-rating.key.json'), JSON.stringify({ note: 'blind id -> source id (M = machine, H = human); not shown to raters', key }, null, 1) + '\n');

  // ---- gold set ----
  const gold = sample(50, 'gold').map(({ c, o }, i) => {
    const R = o.evidence.rules;
    const sents = o.paragraphs.flatMap((p, pi) => p.sentences.map((s, si) => ({ k: `G${i + 1}.${pi}.${si}`, s })));
    return `<div class="card"><p><b>Lá số ${i + 1}/50</b> · ${esc(chartLine(c))}</p>${sents.map(({ k, s }) => `<div class="s" data-k="${k}"><div class="txt">${esc(s.text)}</div>
      <details class="why"><summary>${esc(s.trace.basis === 'he_thong' ? 'lời tổng hợp của hệ thống' : 'căn cứ')} · ${s.trace.rules.length} rule</summary>${s.trace.resolution ? `<div>Phân xử: ${esc(s.trace.resolution.relation)} (${esc(s.trace.resolution.cite ?? '')})</div>` : ''}<ul>${s.trace.rules.map(r => `<li>${esc((R[r]?.cites ?? []).join('; '))} ${esc(R[r]?.reading ?? '')} <code>${esc(r)}</code></li>`).join('')}</ul></details>
      <div class="row">${[['ok', 'đúng'], ['over', 'quá đà'], ['wrong', 'sai'], ['unsure', 'không chắc']].map(([v, l]) => `<label><input type="radio" name="${k}|verdict" value="${v}"> ${l}</label>`).join('')}</div><textarea placeholder="Vì sao? (trang sách, điều kiện bị bỏ sót …)"></textarea></div>`).join('')}</div>`;
  }).join('');
  writeFileSync(join(ROOT, 'docs', 'review', 'prose-gold.html'), page('Bộ vàng: chấm từng câu luận giải cung Mệnh',
    `<p>50 lá số, mỗi câu một lựa chọn: <b>đúng</b> (đúng với lá số và với câu sách được dẫn), <b>quá đà</b> (đúng hướng nhưng nói mạnh hơn sách), <b>sai</b> (sai lá số, sai nghĩa sách, hoặc nói điều sách không nói), <b>không chắc</b>. Mở “căn cứ” để xem rule và trang sách sinh ra câu. Câu “lời tổng hợp của hệ thống” chỉ được nhắc lại ý đã có căn cứ ở trên; nếu nó thêm ý mới, chấm là sai.</p>`,
    gold, 'prose-gold', 'prose-gold.json'));
  console.log(`docs/review/prose-rating.html: ${items.length} paragraphs (${human.length} human); docs/review/prose-gold.html: 50 charts`);
}

function score(ratingFile?: string, goldFile?: string) {
  const lines = ['# Kết quả duyệt văn luận giải cung Mệnh', '', `Tính bởi \`tools/interpret/review_kit.ts score\` · ${new Date().toISOString().slice(0, 10)}`, '', '| Chỉ số | Giá trị | Ngưỡng (plan §6) |', '|---|---|---|'];
  if (ratingFile && existsSync(ratingFile)) {
    const r = read(ratingFile), key = read(join(ROOT, 'docs', 'review', 'prose-rating.key.json')).key as Record<string, string>;
    const rows = Object.entries(r.items as Record<string, { score?: string; guess?: string }>).map(([b, v]) => ({ src: key[b]?.[0], ...v }));
    const m = rows.filter(x => x.src === 'M' && x.score), h = rows.filter(x => x.src === 'H' && x.score);
    const mean = (xs: typeof rows) => xs.length ? (xs.reduce((a, x) => a + Number(x.score), 0) / xs.length).toFixed(2) : '—';
    const fooled = m.filter(x => x.guess).length ? (100 * m.filter(x => x.guess !== 'machine').length / m.filter(x => x.guess).length).toFixed(0) + '%' : '—';
    lines.push(`| Điểm tự nhiên TB, đoạn máy (n=${m.length}) | ${mean(m)} | ≥ 4.0 |`, `| Điểm tự nhiên TB, đoạn người (n=${h.length}) | ${mean(h)} | (đối chứng) |`,
      `| Đoạn máy không bị nhận ra là máy | ${fooled} | ≥ 70% (cần ≥ 15 đoạn người trong bộ) |`);
  }
  if (goldFile && existsSync(goldFile)) {
    const g = read(goldFile), vs = Object.values(g.items as Record<string, { verdict?: string }>).map(x => x.verdict).filter(Boolean) as string[];
    const n = vs.length, c = (v: string) => vs.filter(x => x === v).length;
    lines.push(`| Câu đã chấm (bộ vàng) | ${n} | toàn bộ câu của 50 lá số |`, `| Câu sai hoặc quá đà | ${n ? (100 * (c('wrong') + c('over')) / n).toFixed(1) : '—'}% (sai ${c('wrong')}, quá đà ${c('over')}) | ≤ 3% |`, `| Không chắc | ${c('unsure')} | (xem ghi chú) |`);
  }
  writeFileSync(join(ROOT, 'docs', 'examples', 'prose-review-scores.md'), lines.join('\n') + '\n');
  console.log(lines.join('\n'));
}

const [cmd, a, b] = process.argv.slice(2);
if (cmd === 'pages') pages(); else if (cmd === 'score') score(a, b); else console.log('usage: review_kit.ts pages | score <prose-rating.json> <prose-gold.json>');
