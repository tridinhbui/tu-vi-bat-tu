// Luận chuyên sâu (mức 3) as a Cloudflare Workflow: the whole-chart reading runs as durable steps on Cloudflare, not inside the reader's
// request, so it finishes when the tab is closed or the phone sleeps. Same prompts, check and order as the in-request writer
// (src/chat/deep.ts writeWhole, kept for tests and local runs). Each step stores its result, so a step that fails after the plan does not
// pay for the plan again; a step is retried at most once. Progress is written into the pending deep_readings row (model =
// "pending:<ledger ref>|<label>"), which /api/me/deep/status reports; when the job cannot finish, the spend is refunded and the row cleared.
import { WorkflowEntrypoint, type WorkflowEvent, type WorkflowStep } from "cloudflare:workers";
import { getContainer } from "@cloudflare/containers";
import knowledge from "../interpret/generated/knowledge.json" with { type: "json" };
import type { Knowledge } from "../interpret/types.ts";
import { refund } from "../billing/wallet.ts";
import { SPECS } from "../interpret/chapters.ts";
import { buildContext } from "./context.ts";
import { anthropicLlm, collect, llmErrorLine, CHECK_OPTIONS, DEEP3_OPTIONS, type Llm } from "./llm.ts";
import { CHECK_ASK, CLOSE_ASK, DEEP3_INSTRUCTIONS, OPEN_ASK, PENDING, PLAN_ASK, WHOLE_SECTIONS, sectionAsk, strike } from "./deep.ts";

export interface WholeParams { userId: string; fp: string; key: string; req: Record<string, unknown>; ref: number | null; toYear: number }
interface WholeEnv { DB: D1Database; ANTHROPIC_API_KEY?: string; TVBT: DurableObjectNamespace }

const STEP = { retries: { limit: 1, delay: 30_000, backoff: "constant" as const }, timeout: "10 minutes" as const };

export class DeepWholeWorkflow extends WorkflowEntrypoint<WholeEnv, WholeParams> {
  async run(event: WorkflowEvent<WholeParams>, step: WorkflowStep) {
    const p = event.payload, db = this.env.DB, key = this.env.ANTHROPIC_API_KEY;
    const progress = (label: string) => db.prepare("UPDATE deep_readings SET model = ? WHERE user_id = ? AND fp = ? AND chapter = ? AND text = ''")
      .bind(`${PENDING}${p.ref ?? ""}|${label}`, p.userId, p.fp, p.key).run();
    try {
      if (!key) throw new Error("ANTHROPIC_API_KEY is not set");
      const big: Llm = anthropicLlm(key, DEEP3_OPTIONS), check: Llm = anthropicLlm(key, CHECK_OPTIONS);
      const call = async (llm: Llm, ask: string, context: string) => {
        const r = await collect(llm, { instructions: DEEP3_INSTRUCTIONS, context, messages: [{ role: "user", content: ask }] });
        if (r.stop !== "end_turn" || !r.text.trim()) throw new Error(`step stopped: ${r.stop || "none"}`);
        return r.text.trim();
      };
      const context = await step.do("context", STEP, async () => {
        const res = await getContainer(this.env.TVBT as never, "main").fetch(new Request("https://container/api/facts", {
          method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ...p.req, to_year: p.toYear }) }));
        if (!res.ok) throw new Error(`facts ${res.status}`);
        return buildContext(await res.json(), knowledge as unknown as Knowledge);
      });
      await progress("Đang đọc cả lá số và lập dàn ý");
      const plan = await step.do("plan", STEP, () => call(big, PLAN_ASK, context));
      await progress(`Đang viết và tự kiểm từng phần (0/${WHOLE_SECTIONS.length})`);
      let done = 0;
      const sections = await Promise.all(WHOLE_SECTIONS.map(c => step.do(`section ${c}`, STEP, async () => {
        const draft = await call(big, sectionAsk(c, plan), context);
        const checked = await call(check, CHECK_ASK(draft), context).then(x => strike(draft, x)).catch(() => ({ text: draft, struck: 0 }));
        return checked.text.trim();
      }).then(async s => { await progress(`Đang viết và tự kiểm từng phần (${++done}/${WHOLE_SECTIONS.length})`); return s; })));
      await progress("Đang viết phần mở đầu và mười năm tới");
      const opening = await step.do("opening", STEP, () => call(big, OPEN_ASK(plan), context));
      const close = await step.do("close", STEP, () => call(big, CLOSE_ASK(plan, WHOLE_SECTIONS.map(c => SPECS[c].title).join("; ")), context));
      await step.do("save", STEP, async () => {
        await db.prepare("UPDATE deep_readings SET text = ?, model = ?, created_at = ? WHERE user_id = ? AND fp = ? AND chapter = ?")
          .bind([opening, ...sections, close].join("\n\n"), DEEP3_OPTIONS.model, Date.now(), p.userId, p.fp, p.key).run();
      });
    } catch (e) {
      console.error(llmErrorLine("deep3-workflow", e));
      await step.do("refund", STEP, async () => {
        if (p.ref) await refund(db, p.userId, p.ref).catch(() => false);
        await db.prepare("DELETE FROM deep_readings WHERE user_id = ? AND fp = ? AND chapter = ? AND text = ''").bind(p.userId, p.fp, p.key).run();
      });
    }
  }
}
