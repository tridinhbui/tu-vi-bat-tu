// The model call, behind a small interface so the route can be tested without the network.
import Anthropic from "@anthropic-ai/sdk";

export interface ChatMessage { role: "user" | "assistant"; content: string }
export type LlmEvent = { text: string } | { stop: string };
export interface LlmRequest { instructions: string; context: string; messages: ChatMessage[] }
export type Llm = (req: LlmRequest) => AsyncIterable<LlmEvent>;

export const CHAT_MODEL = "claude-haiku-5-5";

export function anthropicLlm(apiKey: string, model = CHAT_MODEL): Llm {
  const client = new Anthropic({ apiKey, maxRetries: 1 });
  return async function* ({ instructions, context, messages }) {
    const stream = client.messages.stream({
      model, max_tokens: 1200,
      output_config: { effort: "low" },
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
