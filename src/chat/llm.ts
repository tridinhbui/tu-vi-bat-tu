// The model call, behind a small interface so the route can be tested without the network.
import Anthropic from "@anthropic-ai/sdk";

export interface ChatMessage { role: "user" | "assistant"; content: string }
export type LlmEvent = { text: string } | { stop: string };
export interface LlmRequest { instructions: string; context: string; messages: ChatMessage[] }
export type Llm = (req: LlmRequest) => AsyncIterable<LlmEvent>;

export const CHAT_MODEL = "claude-haiku-5-5";
export const DEEP_MODEL = "claude-sonnet-5-5";
/** Luận riêng mức 2 and 3 (Luận sâu, Luận chuyên sâu): the strongest model, thinking over the whole chart (owner, 2026-10-26). */
export const DEEP_MAX_MODEL = "claude-opus-5-5";

/** `thinking`: send `thinking: { type: "adaptive" }` explicitly, so the model reasons over the whole chart before it writes (the deep reading).
 *  `fallback`: a request the model declines on a safety filter is re-run on a fallback model the API picks (server-side, "default" form),
 *  instead of costing the reader a failed reading. */
export interface LlmOptions { model: string; maxTokens: number; effort: "low" | "medium" | "high" | "xhigh"; thinking?: boolean; fallback?: boolean }
// both models think before answering and thinking counts against max_tokens, so leave room above the answer. The deep reading (Luận
// riêng, told to readers as "suy luận sâu") reasons more: effort high and adaptive thinking (owner, 2026-10-25). The chat stays as it was.
export const CHAT_OPTIONS: LlmOptions = { model: CHAT_MODEL, maxTokens: 4000, effort: "low" };
export const DEEP_OPTIONS: LlmOptions = { model: DEEP_MODEL, maxTokens: 16000, effort: "high", thinking: true, fallback: true };
/** Mức 2: one chapter read against the whole chart, 1.500–2.000 words. */
export const DEEP2_OPTIONS: LlmOptions = { model: DEEP_MAX_MODEL, maxTokens: 32000, effort: "high", thinking: true, fallback: true };
/** Mức 3: the whole chart in several steps (plan, one section per life domain, opening and closing); the plan and sections think hardest. */
export const DEEP3_OPTIONS: LlmOptions = { model: DEEP_MAX_MODEL, maxTokens: 32000, effort: "xhigh", thinking: true, fallback: true };
/** Mức 3's check: finds sentences of a section that the chart text does not support (they are struck before the reader sees them). */
export const CHECK_OPTIONS: LlmOptions = { model: DEEP_MODEL, maxTokens: 12000, effort: "medium", thinking: true, fallback: true };

/** The whole answer of one call (no streaming to the reader): its text and why it stopped. */
export async function collect(llm: Llm, req: LlmRequest): Promise<{ text: string; stop: string }> {
  let text = "", stop = "";
  for await (const ev of llm(req)) { if ("text" in ev) text += ev.text; else stop = ev.stop; }
  return { text, stop };
}

/** One line for the Worker log when a model call fails: the API's HTTP status, error type and message (or the error's name and message).
 *  Never the key, the prompt or the user's data. */
export function llmErrorLine(where: string, e: unknown): string {
  if (e instanceof Anthropic.APIError) {
    const body = e.error as { error?: { type?: string; message?: string } } | undefined;
    return `[${where}] Anthropic API error: status=${e.status ?? "none"} type=${body?.error?.type ?? e.name} message=${body?.error?.message ?? e.message}`;
  }
  return `[${where}] model call failed: ${e instanceof Error ? `${e.name}: ${e.message}` : String(e)}`;
}

// `fetch` is for tests only: the real Worker uses the global one
export function anthropicLlm(apiKey: string, { model, maxTokens, effort, thinking, fallback }: LlmOptions, fetch?: typeof globalThis.fetch): Llm {
  const client = new Anthropic({ apiKey, maxRetries: 1, ...(fetch ? { fetch } : {}) });
  return async function* ({ instructions, context, messages }) {
    const params = {
      model, max_tokens: maxTokens,
      output_config: { effort },
      ...(thinking ? { thinking: { type: "adaptive" as const } } : {}),
      // two blocks: the fixed instructions, then this chart's text; the cache breakpoint on the second one lets follow-up messages reuse both
      system: [{ type: "text" as const, text: instructions }, { type: "text" as const, text: context, cache_control: { type: "ephemeral" as const } }],
      messages,
    };
    // the fallback is a beta parameter; its stream has the same text and stop events (a "fallback" block marking the switch is skipped)
    const stream = fallback
      ? client.beta.messages.stream({ ...params, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" })
      : client.messages.stream(params);
    for await (const ev of stream) {
      if (ev.type === "content_block_delta" && ev.delta.type === "text_delta") yield { text: ev.delta.text };
      else if (ev.type === "message_delta" && ev.delta.stop_reason) yield { stop: ev.delta.stop_reason };
    }
  };
}
