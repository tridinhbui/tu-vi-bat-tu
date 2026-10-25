// What a Tarot page may say, and when it must step aside. The banned wording is the one the chapter validator uses (interpret/wording.ts);
// a question about health, pregnancy, life and death, the law or money gets a notice recommending a professional, above the cards.
import { BANNED_WORDS } from "../interpret/wording.ts";

/** Printed at the top of every Tarot page and in every API answer that carries cards. */
export const TAROT_HEADER = "Tarot là công cụ để suy ngẫm, không phải lời dự báo.";

export type Topic = "health" | "pregnancy" | "life" | "legal" | "investment";

/** Lower case, accents and đ folded: Vietnamese is often typed without diacritics. */
export const fold = (s: string) => s.normalize("NFD").replace(/\p{M}/gu, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase();

// Folded patterns match accented and unaccented typing alike; a word that folds onto an everyday one ("tự tử" / "từ từ", "đi tù" /
// "đi tu", "thuốc" / "thuộc", "bệnh" / "bênh") is matched only with its accents, on the lower-cased text.
const TOPICS: Record<Topic, { folded: RegExp; accented?: RegExp }> = {
  health: {
    folded: /\b(bi benh|mac benh|benh tat|benh vien|chua benh|kham benh|om dau|suc khoe|bac si|uong thuoc|thuoc men|don thuoc|chua tri|dieu tri|phau thuat|ca mo|di mo|khoi u|ung thu|xet nghiem|chan doan|trieu chung|nhap vien|tram cam|roi loan lo au)\b/,
    accented: /(^|[^\p{L}])(bệnh|thuốc|mổ)(?!\p{L})/u,
  },
  pregnancy: { folded: /\b(mang thai|co thai|co bau|mang bau|thai nhi|sinh con|de con|sinh no|say thai|pha thai|hiem muon|vo sinh|thu thai|thu tinh)\b/ },
  life: {
    folded: /\b(chet|qua doi|tu sat|song chet|tuoi tho|song duoc bao lau|song bao lau|mat mang|tai nan|tu vong|ket lieu|khong muon song)\b/,
    accented: /(tự tử|tự vẫn)/u,
  },
  legal: {
    folded: /\b(kien tung|khoi kien|bi kien|kien ai|ra toa|toa an|hau toa|luat su|phap ly|phap luat|tranh chap|bi bat|tam giam|cong an|ly hon|ly than|thua ke|di chuc)\b/,
    accented: /(đi tù|ngồi tù|án tù|tù tội|vào tù)/u,
  },
  investment: { folded: /\b(dau tu|co phieu|chung khoan|tien ao|tien dien tu|crypto|bitcoin|coin|forex|ngoai hoi|lo de|xo so|ca cuoc|ca do|vay no|vay tien|vay von|bat dong san|lai suat|danh bac|co bac)\b/ },
};

export const NOTICES: Record<Topic, string> = {
  health: "Câu hỏi của bạn có vẻ liên quan đến sức khỏe. Tarot không thay thế chẩn đoán hay điều trị; hãy hỏi bác sĩ hoặc nhân viên y tế.",
  pregnancy: "Câu hỏi của bạn có vẻ liên quan đến thai sản. Lá bài không trả lời được điều này; hãy hỏi bác sĩ sản khoa hoặc cơ sở y tế.",
  life: "Câu hỏi của bạn có vẻ liên quan đến tính mạng. Lá bài không trả lời câu hỏi này. Nếu bạn hoặc ai đó đang gặp nguy hiểm, hãy gọi cấp cứu 115 hoặc tìm ngay người thân, bác sĩ, chuyên gia tâm lý.",
  legal: "Câu hỏi của bạn có vẻ liên quan đến pháp lý. Lá bài không thay thế tư vấn pháp lý; hãy hỏi luật sư hoặc cơ quan có thẩm quyền.",
  investment: "Câu hỏi của bạn có vẻ liên quan đến đầu tư hay tiền bạc. Lá bài không phải lời khuyên tài chính; hãy hỏi chuyên gia tài chính có giấy phép.",
};

/** The sensitive topics a question touches, in a fixed order. */
export function sensitiveTopics(question: string | null | undefined): Topic[] {
  if (!question) return [];
  const low = question.normalize("NFC").toLowerCase(), f = fold(question);
  return (Object.keys(TOPICS) as Topic[]).filter(t => TOPICS[t].folded.test(f) || !!TOPICS[t].accented?.test(low));
}

export const noticesFor = (question: string | null | undefined) => sensitiveTopics(question).map(t => ({ topic: t, text: NOTICES[t] }));

/** True when a text uses none of the banned wording (a quoted book line “…” is not the site's voice and is not checked). */
export const cleanWording = (text: string) => !BANNED_WORDS.some(b => b.test(text.replace(/“[^”]*”/g, " ")));

/** A question as the server may keep it: trimmed, control characters removed, at most 300 characters; empty means none. */
export function cleanQuestion(q: unknown): string | null {
  if (typeof q !== "string") return null;
  const s = q.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, 300);
  return s || null;
}
