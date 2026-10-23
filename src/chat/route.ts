// POST /api/me/chat — a streamed answer from "Bát Bát". Three modes, by what the body names:
//   {chart_id, messages}  a chart saved in the asker's own account (looked up with the user id, so another user's id finds nothing);
//   {birth, messages}     the chart on screen;
//   {messages}            general mode: no chart facts, a short prompt that says so.
// Order matters: sign-in, validate, get the chart, charge, then call the model; a failure before any text reached the user gives the charge back.
import { cleanReq } from "../auth/charts.ts";
import { COSTS } from "../billing/config.ts";
import { getWallet, refund, spend } from "../billing/wallet.ts";
import type { User } from "../auth/session.ts";
import { buildContext } from "./context.ts";
import { GENERAL_CONTEXT, GENERAL_INSTRUCTIONS, INSTRUCTIONS } from "./prompt.ts";
import type { ChatMessage, Llm } from "./llm.ts";
import type { ChartInput, Knowledge } from "../interpret/types.ts";

export interface ChatDeps {
  /** null for a guest: the panel opens for anyone, but sending needs sign-in (401) */
  db: D1Database; user: User | null; llm: Llm | null; knowledge: Knowledge;
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

export const isChartId = (v: unknown): v is string => typeof v === "string" && /^[a-z0-9]{1,20}$/.test(v);

export async function handleChat(request: Request, d: ChatDeps): Promise<Response> {
  if (request.method !== "POST") return json({ detail: "POST only" }, 405);
  if (!d.user) return json({ detail: "sign in required" }, 401);
  if (request.headers.get("x-tvbt") !== "1") return json({ detail: "missing x-tvbt header" }, 403);
  if (!d.llm) return json({ detail: "chat is not configured" }, 503);
  const user = d.user;
  const body = await request.json().catch(() => null) as { birth?: unknown; chart_id?: unknown; messages?: unknown } | null;
  const messages = cleanMessages(body?.messages);
  const byId = body?.chart_id !== undefined && body?.chart_id !== null, byBirth = body?.birth !== undefined && body?.birth !== null;
  let birth = byBirth ? cleanReq(body!.birth) : null;
  if (!messages || (byId && byBirth) || (byId && !isChartId(body!.chart_id)) || (byBirth && !birth))
    return json({ detail: "body must be {messages} with at most one of {birth} or {chart_id}: up to 20 messages, last from the user, each up to 1500 characters" }, 400);
  if (byId) {
    // only the asker's own saved charts: the lookup is by (user, id), so another user's chart id is simply not found
    const row = await d.db.prepare("SELECT req_json FROM charts WHERE user_id = ? AND id = ?").bind(user.id, body!.chart_id).first<{ req_json: string }>();
    birth = row ? cleanReq(JSON.parse(row.req_json)) : null;
    if (!birth) return json({ detail: "no such saved chart" }, 404);
  }

  // Fail before charging when the lock is the only problem: a locked user sees the lock, not a facts error.
  const before = await getWallet(d.db, user.id, d.now?.());
  if (before.free.remaining <= 0 && before.coins < COSTS.chat) return json({ detail: "locked", wallet: before }, 402);

  let instructions = GENERAL_INSTRUCTIONS, context = GENERAL_CONTEXT;
  if (birth) {
    const nowYear = new Date((d.now?.() ?? Date.now()) + 7 * 3600e3).getUTCFullYear();
    const factsRes = await d.facts({ ...birth.req, to_year: nowYear });
    if (!factsRes.ok) return json({ detail: "could not compute the chart" }, 502);
    const chart = await factsRes.json() as ChartInput;
    instructions = INSTRUCTIONS; context = buildContext(chart, d.knowledge);
  }

  const paid = await spend(d.db, user.id, "chat", d.now?.());
  if (!paid.ok) return json({ detail: "locked", wallet: await getWallet(d.db, user.id, d.now?.()) }, 402);

  const llm = d.llm;
  let cancelled = false;
  const stream = new ReadableStream<Uint8Array>({
    async start(ctl) {
      let delivered = false;
      const giveBack = async () => { try { return await refund(d.db, user.id, paid.ref, d.now?.()); } catch { return false; } };
      ctl.enqueue(sse({ type: "meta", source: paid.source, mode: birth ? "chart" : "general" }));
      try {
        let stop = "";
        for await (const ev of llm({ instructions, context, messages })) {
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
      try { ctl.enqueue(sse({ type: "wallet", wallet: await getWallet(d.db, user.id, d.now?.()) })); ctl.close(); } catch { /* closed */ }
    },
    cancel() { cancelled = true; },
  });
  return new Response(stream, { headers: { "content-type": "text/event-stream; charset=utf-8", "cache-control": "no-store", "x-accel-buffering": "no" } });
}
