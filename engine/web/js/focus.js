// Personal ordering of the reading: the chapters about what the user said matters now (career and relationship status in
// "Thông tin cá nhân") come first, right after the overview. It only moves chapters; no text and no claim depends on it.
// The keys match src/account/profile.ts.
export const CAREER = { hoc: 'Đang đi học', lam: 'Đang đi làm', kinh_doanh: 'Tự kinh doanh hoặc làm chủ', tim_viec: 'Đang tìm việc hoặc muốn đổi việc', nghi: 'Đang nghỉ hoặc đã nghỉ hưu' };
export const RELATIONSHIP = { doc_than: 'Độc thân', tim_hieu: 'Đang tìm hiểu hoặc hẹn hò', ket_hon: 'Đã kết hôn', chia_tay: 'Ly thân hoặc ly hôn' };

// weight 2: a status in motion (looking for work, starting a business, getting to know someone, separating); 1: settled; 0: no reordering
const W_CAREER = { hoc: 1, lam: 1, kinh_doanh: 2, tim_viec: 2, nghi: 0 };
const W_REL = { doc_than: 1, tim_hieu: 2, ket_hon: 1, chia_tay: 2 };
const CHAPTERS = {
  tv: { career: ['cong-danh', 'tai-bach'], rel: ['quan-he'] },
  bt: { career: ['su-nghiep'], rel: ['quan-he'] },
};

/** The focus list for a profile: [{ topic: 'career' | 'rel', label }], strongest first (career first on a tie). */
export function focusOf(profile) {
  if (!profile) return [];
  const out = [];
  if (W_CAREER[profile.career]) out.push({ topic: 'career', w: W_CAREER[profile.career], label: CAREER[profile.career] });
  if (W_REL[profile.relationship]) out.push({ topic: 'rel', w: W_REL[profile.relationship], label: RELATIONSHIP[profile.relationship] });
  return out.sort((a, b) => b.w - a.w);
}

/** Chapter ids of one report ('tv' or 'bt') that the focus brings forward, in order. */
export const focusIds = (prefix, focus) => CHAPTERS[prefix] ? (focus || []).flatMap(f => CHAPTERS[prefix][f.topic]) : [];

/** Moves the focus chapters right after the overview ('tong-quan'), keeping everything else in its order. */
export function orderChapters(chapters, prefix, focus) {
  const ids = focusIds(prefix, focus);
  if (!ids.length) return chapters;
  // Chân dung lá số (the conclusions) stays first, then the overview
  const head = chapters.filter(c => c.id === 'chan-dung' || c.id === 'tong-quan');
  const picked = ids.map(id => chapters.find(c => c.id === id)).filter(Boolean);
  return [...head, ...picked, ...chapters.filter(c => !head.includes(c) && !picked.includes(c))];
}

/** One short line under the overview saying why the order changed and that the content did not. */
export function focusNote(focus, titles) {
  if (!focus?.length) return '';
  const what = focus.map(f => `“${f.label}”`).join(' và ');
  return `<p class="focus-note">Các chương ${titles.join(', ')} được đưa lên trước vì trong <a class="link" href="#tai-khoan" data-go="tai-khoan">Thông tin cá nhân</a> bạn chọn ${what}. Chỉ thứ tự thay đổi; nội dung từng chương giữ nguyên.</p>`;
}
