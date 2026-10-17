// Evidence tier of a finding's rule. Pure (no DOM, no imports) so tests can load it in node.
// MUST stay in step with tier() in tools/build_reference.py: tests/test_evidence_tier.py compares the two on real findings.
export const TIER_TXT = { checked: 'Đã đối chiếu', partial: 'Khớp một phần', sourced: 'Có nguồn', draft: 'Nháp', hypothesis: 'Giả thuyết' };
export const TIER_HINT = {
  checked: 'Có người đã đọc trang sách, quy tắc khớp điều kiện của trang; trích dẫn nguyên văn được máy kiểm lại.',
  partial: 'Đã đối chiếu trang sách: ý chính có trong sách, nhưng quy tắc hẹp hơn, rộng hơn hoặc mạnh hơn trang.',
  sourced: 'Có ghi số trang sách, được diễn đạt lại; chưa được đọc lại riêng từng câu.',
  draft: 'Có sách làm cơ sở nhưng điều kiện hoặc cách vận hành là của hệ thống, hoặc chưa kiểm đủ.',
  hypothesis: 'Không có sách đứng sau (thử nghiệm, quy ước của hệ thống hoặc viết theo trí nhớ).',
};
export const BOOK_NAME = { KL: 'Tử Vi Khảo Luận', TH: 'Tử Vi Thực Hành', TT: 'Tử Vi Đẩu Số Toàn Thư', ZZ: 'Bát Tự Chân Tông', TTT: 'Trích Thiên Tủy' };
// sources that are not a book we hold (build_reference.SRC_BOOK -> EXP, SYS, TBCT). A rule citing only these is a hypothesis.
const NO_BOOK = new Set(['SRC_SYSTEM_STRUCT', 'SRC_EXPERIMENTAL', 'SRC_EXPERIMENTAL_PHI', 'SRC_TVDS_TAN_BIEN', 'SRC_TBCT', 'SRC_ZIPING_ZHENQUAN']);

/** Source ids of a finding, read from the reasoning chain's source nodes (kinds: 'source:SRC_...'). */
export const sourceIdsOf = f => Object.entries(f.why?.kinds || {}).filter(([, k]) => k === 'source').map(([k]) => k.replace(/^source:/, ''));

/** Same decision order as build_reference.tier(). ev = the /api/evidence entry of f.rule_id, or undefined. */
export function tierOf(f, ev) {
  const srcs = sourceIdsOf(f);
  if (!srcs.length || srcs.every(s => NO_BOOK.has(s))) return 'hypothesis';
  if (f.basis !== 'verified') return 'draft';
  if (ev && (ev.verdict === 'faithful' || ev.verdict === 'unsupported_on_page')) return 'checked';
  if (ev && ev.verdict === 'partly') return 'partial';
  return 'sourced';
}

let EV = null; // Map rule_id -> evidence entry; null until loaded (cards then fall back to the old two-way label)
export const evidenceFor = f => EV?.get(f.rule_id);
export const evidenceReady = () => EV !== null;
export function setEvidence(entries) { EV = new Map((entries || []).map(e => [e.rule_id, e])); }
/** Loads GET /api/evidence once. Never throws: without evidence the cards keep their previous labels. */
export async function loadEvidence(fetchFn = fetch) {
  if (EV) return EV;
  try {
    const r = await fetchFn('/api/evidence');
    if (!r.ok) return null;
    setEvidence((await r.json()).entries);
  } catch { /* offline or old server: no evidence layer */ }
  return EV;
}
