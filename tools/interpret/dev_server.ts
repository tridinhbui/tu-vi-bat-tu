// Local stand-in for the Worker, for checking /api/interpret (both modes) without Docker or wrangler:
//   node tools/interpret/dev_server.ts [--port 8768] [--app-dir engine]   (--app-dir: another checkout's engine/, e.g. a clean worktree)
// It starts the Python engine (uvicorn) on PORT+1 and serves the web app on PORT: POST /api/interpret (and /api/overview) goes through
// src/interpret/route.ts — the same handler the Worker uses — with chart facts from the local engine; every other request is proxied.
// TVBT_INTERPRET and TVBT_PROSE_DRAFT default to "1" here (override with the environment).
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { handleInterpret } from '../../src/interpret/route.ts';
import { handleOverview } from '../../src/interpret/overview.ts';
import { BundledStore, LayeredCache } from '../../src/interpret/store.ts';
import type { Knowledge } from '../../src/interpret/types.ts';

const ROOT = join(import.meta.dirname, '..', '..');
const PORT = Number(process.argv[process.argv.indexOf('--port') + 1]) || 8768, PY = PORT + 1;
const ORIGIN = `http://127.0.0.1:${PY}`;
const APP_DIR = process.argv.includes('--app-dir') ? process.argv[process.argv.indexOf('--app-dir') + 1] : 'engine';
const K: Knowledge = JSON.parse(readFileSync(join(ROOT, 'src', 'interpret', 'generated', 'knowledge.json'), 'utf8'));
const store = new BundledStore(K), cache = new LayeredCache({});
const flag = (name: string) => (process.env[name] ?? '1') === '1';

const py = spawn(join(ROOT, '.venv', 'bin', 'python'), ['-m', 'uvicorn', 'tvbt.api:app', '--app-dir', APP_DIR, '--port', String(PY), '--log-level', 'warning'],
  { cwd: ROOT, stdio: 'inherit', env: process.env });
const stop = () => { py.kill(); process.exit(0); };
process.on('SIGINT', stop); process.on('SIGTERM', stop);

async function readBody(req: import('node:http').IncomingMessage): Promise<Buffer> {
  const chunks: Buffer[] = [];
  for await (const c of req) chunks.push(c as Buffer);
  return Buffer.concat(chunks);
}

createServer(async (req, res) => {
  try {
    const body = await readBody(req);
    const url = new URL(req.url ?? '/', `http://localhost:${PORT}`);
    const init = { method: req.method, headers: Object.fromEntries(Object.entries(req.headers).filter(([k]) => !['host', 'connection', 'content-length'].includes(k)) as Array<[string, string]>),
      body: ['GET', 'HEAD'].includes(req.method ?? 'GET') ? undefined : body };
    let out: Response;
    if (url.pathname === '/api/interpret') {
      out = await handleInterpret(new Request(url, init), {
        enabled: flag('TVBT_INTERPRET'), proseDraft: flag('TVBT_PROSE_DRAFT'), reasoner: flag('TVBT_REASONER'), luan: process.env.TVBT_LUAN !== '0',
        facts: birth => fetch(`${ORIGIN}/api/facts`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(birth) }),
        store, cache, defer: p => { p.catch(() => {}); },
      });
    } else if (url.pathname === '/api/overview') {
      out = await handleOverview(new Request(url, init), {
        enabled: flag('TVBT_INTERPRET'), store,
        facts: birth => fetch(`${ORIGIN}/api/facts`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(birth) }),
      });
    } else out = await fetch(`${ORIGIN}${url.pathname}${url.search}`, init);
    res.writeHead(out.status, Object.fromEntries([...out.headers.entries()].filter(([k]) => !['content-encoding', 'content-length', 'transfer-encoding'].includes(k))));
    res.end(Buffer.from(await out.arrayBuffer()));
  } catch (e) {
    res.writeHead(502, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ detail: `dev server: ${(e as Error).message}` }));
  }
}).listen(PORT, () => console.log(`tvbt dev (Worker stand-in) on http://localhost:${PORT}, engine on ${ORIGIN}`));
