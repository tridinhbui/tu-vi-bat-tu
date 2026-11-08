// /api/admin/refine-preview (admin only): the trial of the model refinement layer (owner decision Q5 2026-11-08). GET: a small form;
// POST {birth…, chapters?}: the chosen chapters of the reader's report, each paragraph before and after, with the verifier's verdict.
// Nothing is cached or shown to readers; each POST spends one model call per chapter (the page says so).
import type { ChartInput, Knowledge } from '../types.ts';
import { proseAllChapters } from '../route.ts';
import { checkedOnly } from '../prose/checked.ts';
import { checkInvariants } from '../invariants.ts';
import type { ProseParagraph } from '../prose/realize.ts';
import { refineReport, REFINE_MODEL, REFINE_VERSION, type RefineCall } from './refine.ts';

export interface PreviewDeps { facts: (birth: Record<string, unknown>) => Promise<Response>; knowledge: Knowledge; call: RefineCall; allowDraft: boolean; luan: boolean }
type Ch = { chapter: string; title?: string; paragraphs: ProseParagraph[]; text?: string };

/** The few most mechanical paragraphs of the reader's report, refined in one model call; a refined paragraph that breaks a report-wide
 *  invariant goes back to its draft (the reason is listed). */
export async function refinePreview(facts: ChartInput, k: Knowledge, call: RefineCall, o: { max: number; allowDraft: boolean; luan: boolean }) {
  const all = proseAllChapters(facts, k, { allowDraft: o.allowDraft, deep: true, luan: o.luan }).map(c => checkedOnly(c as never, facts)) as unknown as Ch[];
  const r = await refineReport(all, call, { max: o.max });
  const bad = checkInvariants(facts, r.chapters as never);
  for (const x of r.results) {
    if (!x.ok) continue;
    const p = r.chapters.find(c => c.chapter === x.chapter)!.paragraphs[x.index];
    const hit = bad.filter(v => v.chapter === x.chapter && p.sentences.some(s => s.text === v.text));
    if (hit.length) { x.ok = false; x.reasons.push(...hit.map(v => `${v.inv}: ${v.why}`)); }
  }
  const title = (id: string) => all.find(c => c.chapter === id)?.title ?? id;
  return { model: REFINE_MODEL, version: REFINE_VERSION, usage: r.usage ?? { input: 0, output: 0 }, error: r.error, paragraphs: r.results.length, passed: r.results.filter(x => x.ok).length,
    results: r.results.map(x => ({ ...x, chapterTitle: title(x.chapter) })) };
}

const FORM = `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Thử lớp biên tập văn</title>
<style>:root{--bg:#fbf8f2;--fg:#2a2420;--mut:#7a6f66;--ok:#2f6b3a;--bad:#a3342a;--card:#fff}@media (prefers-color-scheme:dark){:root{--bg:#1c1917;--fg:#ece6df;--mut:#a89e94;--card:#262220;--ok:#7cc48a;--bad:#e8857b}}
body{background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,sans-serif;margin:0;padding:16px;max-width:1100px;margin-inline:auto}h1{font-size:1.3rem}form{display:flex;flex-wrap:wrap;gap:8px;align-items:end}
label{display:flex;flex-direction:column;font-size:.85rem;color:var(--mut)}input,select,button{font:inherit;padding:6px 8px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0;background:var(--card);padding:12px;border-radius:8px}
@media (max-width:700px){.pair{grid-template-columns:1fr}}.tag{font-size:.8rem}.ok{color:var(--ok)}.bad{color:var(--bad)}h3{margin:.2rem 0;font-size:.95rem;color:var(--mut)}p{margin:.3rem 0}.muted{color:var(--mut);font-size:.85rem}</style></head><body>
<h1>Thử lớp biên tập văn (LLM có kiểm)</h1><p class="muted">Mỗi lần chạy gọi mô hình đúng một lần, chỉ cho vài đoạn đọc máy móc nhất (máy tự chọn). Bên trái: bản tất định đang hiện cho người đọc. Bên phải: bản đã biên tập; đoạn trượt bộ kiểm giữ bản tất định, kèm lý do.</p>
<form id="f"><label>Ngày<input name="day" type="number" min="1" max="31" required></label><label>Tháng<input name="month" type="number" min="1" max="12" required></label>
<label>Năm<input name="year" type="number" min="1900" max="2100" required></label><label>Giờ<input name="hour" type="number" min="0" max="23" required></label><label>Phút<input name="minute" type="number" min="0" max="59" value="0"></label>
<label>Giới tính<select name="gender"><option value="male">nam</option><option value="female">nữ</option></select></label><label>Số đoạn tối đa<input name="max" type="number" min="1" max="12" value="6"></label><button>Chạy</button></form>
<div id="out"></div><script>
const f=document.getElementById('f'),out=document.getElementById('out'),e=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
f.onsubmit=async ev=>{ev.preventDefault();const d=Object.fromEntries(new FormData(f));const body={year:+d.year,month:+d.month,day:+d.day,hour:+d.hour,minute:+d.minute,gender:d.gender,to_year:new Date().getFullYear(),max:+d.max};
out.innerHTML='<p class="muted">Đang chạy…</p>';const r=await fetch(location.pathname,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const j=await r.json();if(!r.ok){out.innerHTML='<p class="bad">'+e(j.detail||r.status)+'</p>';return}
out.innerHTML='<p class="muted">'+e(j.model)+' · '+j.passed+'/'+j.paragraphs+' đoạn qua bộ kiểm · '+j.usage.input+' token vào, '+j.usage.output+' token ra</p>'+(j.error?'<p class="bad">'+e(j.error)+'</p>':'')+j.results.map(p=>'<div class="pair"><div><h3>'+e(p.chapterTitle)+' · '+e(p.title||('đoạn '+p.index))+'</h3><p>'+e(p.before)+'</p></div><div><h3 class="tag '+(p.ok?'ok':'bad')+'">'+(p.ok?'qua bộ kiểm':'giữ bản cũ: '+e(p.reasons.join('; ')))+'</h3><p>'+e(p.after||'')+'</p></div></div>').join('')};
</script></body></html>`;

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export async function handleRefinePreview(request: Request, d: PreviewDeps): Promise<Response> {
  if (request.method === 'GET') return new Response(FORM, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
  if (request.method !== 'POST') return json({ detail: 'GET or POST' }, 405);
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body) return json({ detail: 'invalid JSON' }, 400);
  const { max, ...birth } = body;
  const fr = await d.facts(birth);
  if (!fr.ok) return new Response(fr.body, { status: fr.status, headers: fr.headers });
  const facts = await fr.json() as ChartInput;
  return json(await refinePreview(facts, d.knowledge, d.call, { max: Math.min(12, Math.max(1, Number(max) || 6)), allowDraft: d.allowDraft, luan: d.luan }));
}
