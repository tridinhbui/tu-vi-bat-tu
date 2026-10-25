// The model call, behind a small interface so the route can be tested without the network.
import Anthropic from "@anthropic-ai/sdk";

export interface ChatMessage { role: "user" | "assistant"; content: string }
export type LlmEvent = { text: string } | { stop: string };
export interface LlmRequest { instructions: string; context: string; messages: ChatMessage[] }
export type Llm = (req: LlmRequest) => AsyncIterable<LlmEvent>;

export const CHAT_MODEL = "claude-haiku-5-5";
export const DEEP_MODEL = "claude-sonnet-5-5";

/** `thinking`: send `thinking: { type: "adaptive" }` explicitly, so the model reasons over the whole chart before it writes (the deep reading). */
export interface LlmOptions { model: string; maxTokens: number; effort: "low" | "medium" | "high"; thinking?: boolean }
// both models think before answering and thinking counts against max_tokens, so leave room above the answer. The deep reading (Luận
// riêng, told to readers as "suy luận sâu") reasons more: effort high and adaptive thinking (owner, 2026-10-25). The chat stays as it was.
export const CHAT_OPTIONS: LlmOptions = { model: CHAT_MODEL, maxTokens: 4000, effort: "low" };
export const DEEP_OPTIONS: LlmOptions = { model: DEEP_MODEL, maxTokens: 16000, effort: "high", thinking: true };

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
export function anthropicLlm(apiKey: string, { model, maxTokens, effort, thinking }: LlmOptions, fetch?: typeof globalThis.fetch): Llm {
  const client = new Anthropic({ apiKey, maxRetries: 1, ...(fetch ? { fetch } : {}) });
  return async function* ({ instructions, context, messages }) {
    const stream = client.messages.stream({
      model, max_tokens: maxTokens,
      output_config: { effort },
      ...(thinking ? { thinking: { type: "adaptive" as const } } : {}),
      // two blocks: the fixed instructions, then this chart's text; the cache breakpoint on the second one lets follow-up messages reuse both
      system: [{ type: "text", text: instructions }, { type: "text", text: context, cache_control: { type: "ephemeral" } }],
      messages,
    });
    for await (const ev of stream) {
      if (ev.type === "content_block_delta" && ev.delta.type === "text_delta") yield { text: ev.delta.text };
      else if (ev.type === "message_delta" && ev.delta.stop_reason) yield { stop: ev.delta.stop_reason };
    }
  };
}
