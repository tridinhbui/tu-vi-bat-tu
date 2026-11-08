// Model refinement of the deterministic reading (plan docs/plans/THIEN-BAN-33-REVIEW-PLAN.md G10.7, cách 2; owner decision Q5 2026-11-08).
// The deterministic chapter stays the reading; a model may only re-say each paragraph more fluently. One call per chapter, structured
// output: every new sentence names the draft sentences it says. Every paragraph goes through verify.ts; one that fails keeps its draft.
// The style brief is the owner's (docs/plans/NARRATIVE-STYLE-PROMPT.md), held to the reading by the contract below.
import Anthropic from '@anthropic-ai/sdk';
import type { ProseParagraph, ProseSentence } from '../prose/realize.ts';
import { verifyParagraph, type RefinedSentence, type Verdict } from './verify.ts';

export const REFINE_MODEL = 'claude-opus-5-5';
export const REFINE_VERSION = 'refine-0.1.0';
/** Short on purpose (owner, 2026-11-08: "tiết kiệm token hết mức"): the contract and the voice in a few lines. */
export const SYSTEM = `Biên tập lại vài đoạn luận Tử Vi/Bát Tự cho mượt, liền mạch, trang nhã. Chỉ nói lại đúng ý các câu nháp của chính đoạn đó.
Luật: không thêm sao, cung, Hóa, can chi, hành, số, sự kiện, tính cách hay dự đoán; giữ nguyên mọi tên riêng và con số; giữ mọi từ điều kiện (song, nhưng, chưa, dễ, có thể, phần nào, nếu); không nâng mức chắc chắn; câu sách giữ sát lời; độ dài gần bằng nháp.
Không dùng: sách, trang, căn cứ, quy tắc, nhận định, hệ thống, chắc chắn, cả đời, suốt đời, không bao giờ, "Bên cạnh đó", "Ngoài ra", "Điều này cho thấy", "không phải … mà là …".
Vào: "#<mã đoạn>" rồi mỗi câu nháp một dòng "<số>. <câu>". Ra: "#<mã đoạn>" rồi mỗi câu mới một dòng "<các số câu nháp nó nói, cách bằng dấu phẩy>| <câu mới>". Mọi câu nháp phải được nói lại. Không viết gì khác.`;

export interface ParagraphResult { chapter: string; index: number; title?: string; ok: boolean; reasons: string[]; before: string; after?: string }
type Ch = { chapter: string; paragraphs: ProseParagraph[]; text?: string };
/** the model call: one chapter's request text in, the JSON text out (a function so tests run without the network) */
export type RefineCall = (system: string, user: string) => Promise<{ text: string; usage?: { input: number; output: number } }>;

/** Habitual openings of the deterministic prose (the owner's list, docs/plans/NARRATIVE-STYLE-PROMPT.md §3). */
const HABIT = /^(Bên cạnh đó|Ngoài ra|Thêm vào đó|Điều này|Song song với|Cũng vì vậy|Cùng thế ấy|Cũng từ thế ấy|Thêm một|Hơn nữa|Mặt khác)/u;
/** How mechanical a paragraph reads: habitual openings, sentences opening with the same word, runs of short sentences. A main paragraph of
 *  three to eight sentences only (not a Đọc sâu fold, not the neutral severity lines). */
export function polishScore(p: ProseParagraph): number {
  const ss = p.sentences;
  // the main reading only: the Tử Vi Đọc sâu fold (deep) and the Bát Tự one (depth 'sau') stay as they are
  if (p.deep || p.severity || (p as ProseParagraph & { depth?: string }).depth === 'sau' || ss.length < 3 || ss.length > 8) return 0;
  const first = ss.map(s => s.text.split(/\s+/)[0]);
  let score = ss.filter(s => HABIT.test(s.text)).length;
  score += first.length - new Set(first).size;
  for (let i = 1; i < ss.length; i++) if (ss[i].text.split(/\s+/).length < 9 && ss[i - 1].text.split(/\s+/).length < 9) score++;
  return score;
}
/** The few paragraphs of a report worth a model pass (owner, 2026-11-08: "LLM hạn chế một số chỗ nhỏ thôi"): the most mechanical ones,
 *  at most `max`, each scoring at least 2. */
export function selectParagraphs(chs: Ch[], max = 6): Array<{ c: number; p: number }> {
  return chs.flatMap((ch, c) => ch.paragraphs.map((p, i) => ({ c, p: i, score: polishScore(p) }))).filter(x => x.score >= 2)
    .sort((a, b) => b.score - a.score || a.c - b.c || a.p - b.p).slice(0, max).map(({ c, p }) => ({ c, p }));
}
/** The request: "#c.p" then the numbered draft sentences, nothing else. */
export function reportRequest(chs: Ch[], picks: Array<{ c: number; p: number }>): string {
  return picks.map(({ c, p }) => [`#${c}.${p}`, ...chs[c].paragraphs[p].sentences.map((s, j) => `${j}. ${s.text}`)].join('\n')).join('\n\n');
}
/** The answer: "#c.p" blocks of "i,j| sentence" lines; a malformed line makes its paragraph fail (verify.ts then keeps the draft). */
export function parseAnswer(text: string): Map<string, RefinedSentence[]> {
  const out = new Map<string, RefinedSentence[]>();
  let cur: RefinedSentence[] | null = null;
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    const h = line.match(/^#\s*(\d+\.\d+)/);
    if (h) { cur = []; out.set(h[1], cur); continue; }
    const m = line.match(/^([\d,\s]+)\|\s*(.+)$/);
    if (cur) cur.push(m ? { src: m[1].split(',').map(x => Number(x.trim())).filter(x => !Number.isNaN(x)), text: m[2] } : { src: [], text: line });
  }
  return out;
}

/** A new paragraph from verified sentences: each new sentence carries the merged trace of the draft sentences it says, marked refined. */
function assemble(p: ProseParagraph, out: RefinedSentence[]): ProseParagraph {
  const sentences: ProseSentence[] = out.map(o => {
    const src = o.src.map(i => p.sentences[i]), first = src[0];
    const uniq = (xs: string[]) => [...new Set(xs)];
    const basis = src.some(s => s.trace.basis === 'sach') ? 'sach' : first.trace.basis;
    return { text: o.text.trim(), trace: { ...first.trace, basis, rules: uniq(src.flatMap(s => s.trace.rules)), cites: uniq(src.flatMap(s => s.trace.cites)),
      concepts: uniq(src.flatMap(s => s.trace.concepts)), refined: { from: o.src, version: REFINE_VERSION } } } as ProseSentence;
  });
  return { ...p, sentences, text: sentences.map(s => s.text).join(' '), refined: true } as ProseParagraph;
}

/** The report with its few chosen paragraphs refined by one model call: a paragraph that passes verify.ts is replaced, the others keep
 *  their draft; the result lists each verdict. */
export async function refineReport<T extends Ch>(chs: T[], call: RefineCall, o: { max?: number } = {}): Promise<{ chapters: T[]; results: ParagraphResult[]; usage?: { input: number; output: number }; error?: string }> {
  const picks = selectParagraphs(chs, o.max ?? 6);
  if (!picks.length) return { chapters: chs, results: [] };
  let answer: Map<string, RefinedSentence[]>, usage: { input: number; output: number } | undefined;
  try {
    const r = await call(SYSTEM, reportRequest(chs, picks));
    usage = r.usage; answer = parseAnswer(r.text);
  } catch (e) {
    return { chapters: chs, results: [], error: e instanceof Error ? `${e.name}: ${e.message}` : String(e) };
  }
  const results: ParagraphResult[] = [];
  const out = chs.map((ch, c) => {
    if (!picks.some(x => x.c === c)) return ch;
    const paragraphs = ch.paragraphs.map((p, i) => {
      if (!picks.some(x => x.c === c && x.p === i)) return p;
      const got = answer.get(`${c}.${i}`);
      const v: Verdict = got ? verifyParagraph(p.sentences, got) : { ok: false, reasons: ['đoạn không có trong kết quả'] };
      results.push({ chapter: ch.chapter, index: i, title: p.title, ok: v.ok, reasons: v.reasons, before: p.text, ...(got ? { after: got.map(s => s.text).join(' ') } : {}) });
      return v.ok ? assemble(p, got!) : p;
    });
    return { ...ch, paragraphs, text: paragraphs.map(p => p.text).join('\n\n') };
  });
  return { chapters: out, results, usage };
}

/** The Claude call: Opus 5.5 at low effort (thinking cannot be turned off on this model; low keeps it short), plain-text answer, a small
 *  output cap, server-side fallback on a refusal. The system prompt is too short to cache, so no cache breakpoint. */
export function claudeRefineCall(apiKey: string, fetchImpl?: typeof globalThis.fetch): RefineCall {
  const client = new Anthropic({ apiKey, maxRetries: 1, ...(fetchImpl ? { fetch: fetchImpl } : {}) });
  return async (system, user) => {
    const msg = await client.beta.messages.create({
      model: REFINE_MODEL, max_tokens: 6000, betas: ['server-side-fallback-2026-07-01'], fallbacks: 'default',
      output_config: { effort: 'low' }, system, messages: [{ role: 'user', content: user }],
    });
    if (msg.stop_reason === 'refusal') throw new Error(`refusal (${msg.stop_details?.category ?? 'no category'})`);
    if (msg.stop_reason === 'max_tokens') throw new Error('max_tokens: the answer was cut');
    const text = msg.content.flatMap(b => (b.type === 'text' ? [b.text] : [])).join('');
    return { text, usage: { input: msg.usage.input_tokens, output: msg.usage.output_tokens } };
  };
}
