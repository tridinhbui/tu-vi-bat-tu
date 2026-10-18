// One "session" = what the browser does for one visitor: claims + rules (meta), chart + reasoning + analysis (in parallel), then year.
const [base, N, variant, seed] = [process.argv[2], +process.argv[3], process.argv[4], +(process.argv[5] || 1)];
let s = seed; const rnd = () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
const birth = () => ({ year: 1940 + Math.floor(rnd() * 70), month: 1 + Math.floor(rnd() * 12), day: 1 + Math.floor(rnd() * 28), hour: Math.floor(rnd() * 24), minute: 0, gender: rnd() < .5 ? 'male' : 'female', level: 3 });
const t0 = performance.now();
async function call(u, body) { const t = performance.now(); try { const r = await fetch(base + u, body ? { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) } : {}); await r.arrayBuffer(); return { u, ms: performance.now() - t, st: r.status }; } catch (e) { return { u, ms: performance.now() - t, st: 0, msg: String(e.cause?.code || e.message) }; } }
async function session() {
  const b = birth(), start = performance.now();
  const meta = (variant === 'base' || variant === 'optB') ? [call('/api/claims'), call('/api/rules')] : [];
  const main = [call('/api/chart', b), call('/api/reasoning', b), call('/api/analysis', b)];
  const rs = await Promise.all([...meta, ...main]);
  const ttr = performance.now() - start;
  // the result page asks /api/year 4x for the same birth/year in the current frontend (2 summary cards + 2 year explorers); 1x with request de-duplication
  const yearCalls = variant === 'opt' ? 1 : 4;
  const ys = await Promise.all(Array.from({ length: yearCalls }, () => call('/api/year', { ...b, to_year: 2026 })));
  return { ttr, rs: [...rs, ...ys] };
}
const out = await Promise.all(Array.from({ length: N }, session));
const makespan = performance.now() - t0, all = out.flatMap(o => o.rs);
const q = (a, p) => { a = [...a].sort((x, y) => x - y); return a[Math.min(a.length - 1, Math.floor(p * a.length))]; };
const ttr = out.map(o => o.ttr), by = {};
all.forEach(r => (by[r.u] ||= []).push(r.ms));
console.log(JSON.stringify({ N, variant, makespan_s: +(makespan / 1000).toFixed(2), ttr_p50_s: +(q(ttr, .5) / 1000).toFixed(2), ttr_p95_s: +(q(ttr, .95) / 1000).toFixed(2), ttr_max_s: +(Math.max(...ttr) / 1000).toFixed(2), sessions_per_min: +(N / (makespan / 60000)).toFixed(1), requests: all.length, errors: all.filter(r => r.st !== 200).length, err_detail: all.filter(r => r.st !== 200).slice(0, 3).map(r => `${r.u}:${r.st}:${r.msg || ''}`), over30s: ttr.filter(t => t > 30000).length, p50_ms: Object.fromEntries(Object.entries(by).map(([k, v]) => [k.replace('/api/', ''), Math.round(q(v, .5))])) }));
