// POST /api/me/chat — a streamed answer about the user's own chart. Order matters: validate, get the chart, charge, then call the model;
// a failure before any text reached the user gives the charge back.
import { cleanReq } from "../auth/charts.ts";
import { COSTS } from "../billing/config.ts";
import { getWallet, refund, spend } from "../billing/wallet.ts";
import type { User } from "../auth/session.ts";
import { buildContext } from "./context.ts";
import { INSTRUCTIONS } from "./prompt.ts";
import type { ChatMessage, Llm } from "./llm.ts";
import type { ChartInput, Knowledge } from "../interpret/types.ts";

export interface ChatDeps {
  db: D1Database; user: User; llm: Llm | null; knowledge: Knowledge;
  facts: (birth: Record<string, unknown>) => Promise<Response>;
  now?: () => number;
}

const MAX_MESSAGES = 20, MAX_CHARS = 1500, MAX_TOTAL = 12000;
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const sse = (o: unknown) => new TextEncoder().encode(`data: ${JSON.stringify(o)}\n\n`);

export function cleanMessages(x: unknown): ChatMessage[] | null {
  if (!Array.isArray(x) || x.length === 0 || x.length > MAX_MESSAGES) return null;
  const out: ChatMessage[] = []; let total = 0;
  for (const m of x) {
    if (!m || typeof m !== "object") return null;
    const { role, content } = m as Record<string, unknown>;
    if ((role !== "user" && role !== "assistant") || typeof content !== "string") return null;
    const text = content.trim();
    if (!text || text.length > MAX_CHARS) return null;
    total += text.length;
    out.push({ role, content: text });
  }
  // the API wants the first message from the user, and we answer the last one
  if (out[0].role !== "user" || out[out.length - 1].role !== "user" || total > MAX_TOTAL) return null;
  return out;
}

export async function handleChat(request: Request, d: ChatDeps): Promise<Response> {
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  if (request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  if (!d.llm) return json({ detail: "chat is not configured" }, 503);
  const body = await request.json().catch(() => null) as { birth?: unknown; messages?: unknown } | null;
  const birth = cleanReq(body?.birth), messages = cleanMessages(body?.messages);
  if (!birth || !messages) return json({ detail: "body must be {birth, messages}: up to 20 messages, last from the user, each up to 1500 characters" }, 400);

  // Fail before charging when the lock is the only problem: a locked user sees the lock, not a facts error.
  const before = await getWallet(d.db, d.user.id, d.now?.());
  if (before.free.remaining <= 0 && before.coins < COSTS.chat) return json({ detail: "locked", wallet: before }, 402);

  const nowYear = new Date((d.now?.() ?? Date.now()) + 7 * 3600e3).getUTCFullYear();
  const factsRes = await d.facts({ ...birth.req, to_year: nowYear });
  if (!factsRes.ok) return json({ detail: "could not compute the chart" }, 502);
  const chart = await factsRes.json() as ChartInput;
  const context = buildContext(chart, d.knowledge);

  const paid = await spend(d.db, d.user.id, "chat", d.now?.());
  if (!paid.ok) return json({ detail: "locked", wallet: await getWallet(d.db, d.user.id, d.now?.()) }, 402);

  const llm = d.llm;
  let cancelled = false;
  const stream = new ReadableStream<Uint8Array>({
    async start(ctl) {
      let delivered = false;
      const giveBack = async () => { try { return await refund(d.db, d.user.id, paid.ref, d.now?.()); } catch { return false; } };
      ctl.enqueue(sse({ type: "meta", source: paid.source }));
      try {
        let stop = "";
        for await (const ev of llm({ instructions: INSTRUCTIONS, context, messages })) {
          if (cancelled) return;
          if ("text" in ev) { if (ev.text) { delivered = true; ctl.enqueue(sse({ type: "delta", text: ev.text })); } }
          else stop = ev.stop;
        }
        if (!delivered) {
          // nothing came back (a refusal or an empty answer): the user got nothing, so they are not charged
          const refunded = await giveBack();
          ctl.enqueue(sse({ type: "error", message: stop === "refusal" ? "Trợ lý không trả lời được câu này. Bạn thử hỏi theo cách khác nhé." : "Chưa nhận được câu trả lời. Bạn thử lại nhé.", refunded }));
        } else ctl.enqueue(sse({ type: "done", truncated: stop === "max_tokens" }));
      } catch {
        const refunded = delivered ? false : await giveBack();
        try { ctl.enqueue(sse({ type: "error", message: "Trợ lý đang gặp sự cố. Bạn thử lại sau nhé.", refunded })); } catch { /* the client is gone */ }
      }
      try { ctl.enqueue(sse({ type: "wallet", wallet: await getWallet(d.db, d.user.id, d.now?.()) })); ctl.close(); } catch { /* closed */ }
    },
    cancel() { cancelled = true; },
  });
  return new Response(stream, { headers: { "content-type": "text/event-stream; charset=utf-8", "cache-control": "no-store", "x-accel-buffering": "no" } });
}
