// The real Anthropic client (llm.ts) against a fake Messages API: what is sent, and how the streamed answer comes back.
import { test } from "node:test";
import assert from "node:assert/strict";
import { anthropicLlm, CHAT_MODEL, CHAT_OPTIONS, DEEP_MODEL, DEEP_OPTIONS, type LlmEvent } from "../llm.ts";

const sse = (events: object[]) => events.map(e => `event: ${(e as any).type}\ndata: ${JSON.stringify(e)}\n\n`).join("");
const answer = (texts: string[], stop = "end_turn") => sse([
  { type: "message_start", message: { id: "msg_1", type: "message", role: "assistant", model: CHAT_MODEL, content: [], stop_reason: null, stop_sequence: null, usage: { input_tokens: 10, output_tokens: 0 } } },
  { type: "content_block_start", index: 0, content_block: { type: "thinking", thinking: "", signature: "" } },
  { type: "content_block_delta", index: 0, delta: { type: "thinking_delta", thinking: "" } },
  { type: "content_block_stop", index: 0 },
  { type: "content_block_start", index: 1, content_block: { type: "text", text: "" } },
  ...texts.map(text => ({ type: "content_block_delta", index: 1, delta: { type: "text_delta", text } })),
  { type: "content_block_stop", index: 1 },
  { type: "message_delta", delta: { stop_reason: stop, stop_sequence: null }, usage: { output_tokens: 5 } },
  { type: "message_stop" },
]);

function fakeApi(body: string, status = 200) {
  const seen: { url: string; headers: Headers; body: any }[] = [];
  const fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const req = new Request(input, init);
    seen.push({ url: req.url, headers: req.headers, body: JSON.parse(await req.text()) });
    return new Response(body, { status, headers: { "content-type": status === 200 ? "text/event-stream" : "application/json" } });
  }) as typeof globalThis.fetch;
  return { fetch, seen };
}
const drain = async (it: AsyncIterable<LlmEvent>) => { const out: LlmEvent[] = []; for await (const e of it) out.push(e); return out; };
const req = { instructions: "HƯỚNG DẪN", context: "LÁ SỐ", messages: [{ role: "user" as const, content: "Công danh của tôi?" }] };

test("the chat call goes to the Messages API with the key in a header, the chart in a cached system block, and streams", async () => {
  const api = fakeApi(answer(["Cung Quan ", "có Tử Vi."]));
  const out = await drain(anthropicLlm("sk-test", CHAT_OPTIONS, api.fetch)(req));
  assert.deepEqual(out, [{ text: "Cung Quan " }, { text: "có Tử Vi." }, { stop: "end_turn" }]);   // thinking blocks are not shown
  assert.equal(api.seen.length, 1);
  const { url, headers, body } = api.seen[0];
  assert.match(url, /^https:\/\/api\.anthropic\.com\/v1\/messages/);
  assert.equal(headers.get("x-api-key"), "sk-test");
  assert.equal(JSON.stringify(body).includes("sk-test"), false);
  assert.equal(body.model, CHAT_MODEL); assert.equal(body.stream, true);
  assert.equal(body.max_tokens, CHAT_OPTIONS.maxTokens); assert.deepEqual(body.output_config, { effort: "low" });
  assert.deepEqual(body.system, [{ type: "text", text: "HƯỚNG DẪN" }, { type: "text", text: "LÁ SỐ", cache_control: { type: "ephemeral" } }]);
  assert.deepEqual(body.messages, req.messages);
});

test("the deep reading uses its own model and budget, and a truncated answer reports max_tokens", async () => {
  const api = fakeApi(answer(["Chương"], "max_tokens"));
  const out = await drain(anthropicLlm("sk-test", DEEP_OPTIONS, api.fetch)(req));
  assert.deepEqual(out.at(-1), { stop: "max_tokens" });
  assert.equal(api.seen[0].body.model, DEEP_MODEL); assert.equal(api.seen[0].body.max_tokens, DEEP_OPTIONS.maxTokens);
});

test("an API error is thrown, so the route can refund", async () => {
  const api = fakeApi(JSON.stringify({ type: "error", error: { type: "authentication_error", message: "invalid x-api-key" } }), 401);
  await assert.rejects(drain(anthropicLlm("sk-bad", CHAT_OPTIONS, api.fetch)(req)));
});
