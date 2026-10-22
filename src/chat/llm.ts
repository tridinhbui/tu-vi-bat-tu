// The model call, behind a small interface so the route can be tested without the network.
import Anthropic from "@anthropic-ai/sdk";

export interface ChatMessage { role: "user" | "assistant"; content: string }
export type LlmEvent = { text: string } | { stop: string };
export interface LlmRequest { instructions: string; context: string; messages: ChatMessage[] }
export type Llm = (req: LlmRequest) => AsyncIterable<LlmEvent>;

export const CHAT_MODEL = "claude-haiku-5-5";
export const DEEP_MODEL = "claude-sonnet-5-5";

export interface LlmOptions { model: string; maxTokens: number; effort: "low" | "medium" | "high" }
// both models think before answering (adaptive thinking is on by default) and thinking counts against max_tokens, so leave room above the answer
export const CHAT_OPTIONS: LlmOptions = { model: CHAT_MODEL, maxTokens: 4000, effort: "low" };
export const DEEP_OPTIONS: LlmOptions = { model: DEEP_MODEL, maxTokens: 12000, effort: "medium" };

// `fetch` is for tests only: the real Worker uses the global one
export function anthropicLlm(apiKey: string, { model, maxTokens, effort }: LlmOptions, fetch?: typeof globalThis.fetch): Llm {
  const client = new Anthropic({ apiKey, maxRetries: 1, ...(fetch ? { fetch } : {}) });
  return async function* ({ instructions, context, messages }) {
    const stream = client.messages.stream({
      model, max_tokens: maxTokens,
      output_config: { effort },
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
