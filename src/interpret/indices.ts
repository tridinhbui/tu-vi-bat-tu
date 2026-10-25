// System indices for the "Tổng quan lá số" charts (docs/PRODUCT-PLAN.md phase 1.1–1.4). Two different things are measured, and kept apart:
//
//   1. the NATAL quality of each palace (the radar): verified natal findings of the rule engine (engine.ts) on the palace and its tam phương,
//      told as a ratio to the mean of the same palace over the 1,000-chart corpus. This never moves with time.
//   2. how a PERIOD (đại vận, year, month) reads in the books. Each period is a sum of layers; every layer is a raw net value (support −
//      limit of its items, each item a book sentence or a star with its page, or a labelled convention) divided by its typical size over
//      corpus1000 (root mean square, engine/data/kg/index_norms.json, tools/interpret/index_norms.ts). The raw value is NOT centred: a layer
//      with no item adds 0, so silence is never read as bad or good (indices-3.0.0, owner's decision 2026-10-24). The sum is placed on five
//      levels by the corpus quantiles of the periods with book evidence (12 / 33 / 67 / 88 %). A period with no book item at all is told "Trung bình" with the flag
//      `insufficient` ("chưa đủ căn cứ"), never as a real middle; a month with nothing of its own to read has no level of its own.
//      Book layers decide the direction; convention layers only modulate it (conventionCap). Natal findings are never a period's reasons.
//
// Đại vận layers
//   van      the book sentences about the vận palace: Khảo Luận pp.233-236 and Thực Hành pp.115-117 (van_han_rules.json, by rule id), Khảo
//            Luận pp.230-233 (tam hợp of the vận against the birth year; the Thái Tuế – Quan Phù – Bạch Hổ triad of p.233), Toàn Thư pp.97-105
//            nhập hạn ca (paraphrased, page check pending: ×0.5); and KL p.233 mục 3-4: the đắc / hãm of the chính tinh, trung tinh and hung
//            tinh of the vận palace, its xung chiếu and tam hợp, and its nhị hợp when that palace generates the vận (each star half a sentence).
//   hoa_van  the Tứ Hóa of the decade stem (facts.decades[].hoa) landing on the decade palace, its tam phương or Mệnh. Common convention
//            (phi hóa theo can đại vận); the three books give no sentence for it, so its items are labelled thong_le.
//   TH p.118 (Mệnh / Thân sáng sủa or hắc ám against the hạn) is told in the decade's words, never added to the score: the book names the
//   cách of a good hạn on either kind of Mệnh and says nothing for a bad hạn on a dark one.
// Year layers
//   dai_van       the score of the đại vận the year falls in.
//   tieu_han      the book sentences and the đắc / hãm of the tiểu hạn palace (KL p.40: read the stars of the tiểu vận palace with its phối
//                 chiếu). Tiểu hạn: age 1 by the birth-year triad, direction by the chart's school (KL pp.39-40 âm dương by default).
//   luu_dai_han   the same reading of the year's lưu đại hạn palace (TH pp.117-118: "để đoán và phối hợp với năm Tiểu hạn").
//   luu_sao       Thực Hành tr.114: lưu Khốc, Hư meeting the tiểu hạn are bad, with hung tinh "năm đầy tai ương" (positions KL tr.41-42).
//   luu_sao_tl    the other lưu stars in reach (Kình, Đà as sát tinh, Lộc Tồn; Khốc, Hư off the tiểu hạn): side of their kind, convention.
//                 KL tr.41: the lưu stars are "nhất thời, không nặng ký" — hence the low weights.
//   luu_tu_hoa    the Tứ Hóa of the year stem on the tiểu hạn's tam phương or Mệnh: convention, not in the three books (low weight, labelled);
//                 left out when the year stem is the decade stem (the same four stars are already in the decade).
// Month: the viewed year's score plus the đắc / hãm of the stars of the nguyệt hạn palace and its tam phương (position TH p.115, KL pp.40-41).
//
// Bát Tự strip: the luck pillars of the Bát Tự chart on the same time axis, tagged by whether they carry the điều hậu stems of Thiệu Vĩ Hoa's
// table (TVH pp.389-396, via facts.bazi.deep). It is shown beside the decades, never added to the Tử Vi score.
import type { ChartInput, Knowledge, Palace, Rule } from './types.ts';
import { run } from './engine.ts';
import { triggerAtoms } from './kg/atoms.ts';
import type { World } from './dsl.ts';
import { Geo, SCOPE_WEIGHT, TIER_WEIGHT, atomSeat, rarity, type Tier } from './reason/tiers.ts';
import { guardHolds } from './reason/positions.ts';
import { SAT } from './reason/structures.ts';
import { toanThuLines } from './prose/vanhan_books.ts';


export const INDICES_VERSION = 'indices-3.2.0';
export const DISCLAIMER = 'Mức tổng hợp từ câu sách và thông lệ có ghi nhãn, so với 1.000 lá số mẫu; không phải xác suất hay dự báo.';

export type Side = 'support' | 'limit';
export type Layer = 'ban_menh' | 'hoa_van' | 'van' | 'dai_van' | 'dau_tinh' | 'tieu_han' | 'luu_dai_han' | 'luu_sao' | 'luu_sao_tl' | 'luu_tu_hoa' | 'thong_le_cap' | 'nam' | 'nguyet';
/** sach: a book sentence with its page; sach_dien_giai: a paraphrased book passage whose page is still to be checked; thong_le: convention;
 *  nhap: an experimental definition (draft cách cục) */
export type ItemBasis = 'sach' | 'sach_dien_giai' | 'thong_le' | 'nhap';
export type Rel = 'self' | 'opp' | 'trine' | 'nhi_hop' | 'menh';
export interface Item {
  id: string; side: Side; w: number; layer: Layer; palace: string; scope: Rel; cite: string; text: string; basis: ItemBasis;
  /** the reading as a clause for the period sentences ("vận có Tham Lang ở Dậu thì hao tài, phóng túng") and its book */
  gist?: string; book?: string;
  /** a star read by its brightness (KL p.233 mục 4): the star and its printed level */
  star?: string; dignity?: string;
}

const r3 = (x: number) => Math.round(x * 1000) / 1000;
/** A number as Vietnamese text: decimal comma, two places. */
const vn = (x: number) => String(Math.round(x * 100) / 100).replace('.', ',');
const STEMS = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'];
const BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'];
const REL_OF: Record<number, 'self' | 'opp' | 'trine'> = { 0: 'self', 6: 'opp', 4: 'trine', 8: 'trine' };
/** Distance weights of a period item: the reasoner's scope weights; nhị hợp as a tam hợp, Mệnh (when outside the tam phương) 0.6 — system convention. */
export const REL_W: Record<Rel, number> = { self: SCOPE_WEIGHT.self, opp: SCOPE_WEIGHT.opp, trine: SCOPE_WEIGHT.trine, nhi_hop: SCOPE_WEIGHT.trine, menh: 0.6 };
/** What each palace is about (engine/tvbt/van_han.py DOMAIN, the topic the tiểu hạn reading already names). */
export const DOMAIN: Record<string, string> = { 'Mệnh': 'chính mình', 'Phụ Mẫu': 'cha mẹ, người bề trên', 'Phúc Đức': 'đời sống tinh thần, họ hàng',
  'Điền Trạch': 'nhà cửa, đất đai', 'Quan Lộc': 'công danh, sự nghiệp', 'Nô Bộc': 'bạn bè, người cộng tác', 'Thiên Di': 'giao thiệp bên ngoài, đi xa',
  'Tật Ách': 'thể trạng', 'Tài Bạch': 'tiền bạc', 'Tử Tức': 'con cái', 'Phu Thê': 'hôn nhân', 'Huynh Đệ': 'anh chị em' };

// ---- the side of each vận reading, as its book sentence states it (weights: 1 plain, 0.5 when the sentence is conditional or mild) ----
/** Khảo Luận pp.233-236 / Thực Hành pp.115-117 (engine/data/van_han_rules.json) by rule id. VH_THAI_TUE, VH_QUAN_PHU, VH_BACH_HO are one
 *  sentence of KL p.233 ("Vị trí tam hợp Thái tuế, Quan phù, Bạch hổ là vị trí may mắn và tốt hạnh nhất … bất kể Mệnh đóng ở vị trí nào,
 *  đương số cũng thịnh phát"): the same weight for the three (before 3.0.0 Quan Phù and Bạch Hổ weighed half). */
export const VAN_RULES: Record<string, { side: Side; w: number }> = {
  VH_TPVT_SAT: { side: 'support', w: 1 }, VH_TPVT_CNDL: { side: 'limit', w: 1 }, VH_VCD_SPT: { side: 'support', w: 1 },
  VH_TUAN_TRIET: { side: 'support', w: 1 }, VH_NN_DAO_HONG: { side: 'support', w: 0.5 }, VH_NN_KINH_DA: { side: 'limit', w: 1 },
  VH_CU_NHAT_SPT: { side: 'support', w: 1 }, VH_CNDL_TOT: { side: 'support', w: 1 }, VH_CNDL_XAU: { side: 'limit', w: 1 },
  VH_VT_TP: { side: 'support', w: 1 }, VH_VT_SPT: { side: 'support', w: 1 }, VH_THAI_TUE: { side: 'support', w: 1 },
  VH_QUAN_PHU: { side: 'support', w: 1 }, VH_BACH_HO: { side: 'support', w: 1 },
  VH_POS_1: { side: 'support', w: 1 }, VH_POS_2: { side: 'limit', w: 1 }, VH_POS_3: { side: 'support', w: 1 }, VH_POS_4: { side: 'limit', w: 1 },
  VH_POS_5: { side: 'support', w: 1 }, VH_POS_6: { side: 'limit', w: 1 },
  TH_TPVT_LOC_TA_HUU: { side: 'support', w: 1 }, TH_NDCC_HOA3: { side: 'support', w: 1 }, TH_CU_NHAT_SONG_LOC: { side: 'support', w: 1 },
  TH_CNDL_TAM_HOA: { side: 'support', w: 1 }, TH_SPLT_KINH_DOANH: { side: 'support', w: 1 }, TH_DAO_HONG_KHOA_QUYEN: { side: 'support', w: 1 },
  TH_TPVT_KHONG_KIEP_KY: { side: 'limit', w: 1 }, TH_NDCC_KHONG_KIEP: { side: 'limit', w: 1 },
  // TH p.115 IX.6 ("rất kỵ"), IX.9 ("rất hại"), IX.10 ("hoạnh phát"), p.117 6n ("tất gặp lắm tai ương"; IX.9 and 6n are told "rất bất
  // lợi", owner 2026-10-24), indices-3.1.0; IX.10's other
  // half ("không hề gì") is in VAN_NO_SIDE and takes back the Kình / Đà hãm in dhItems (KL233_HAM_TH115_IX10). The page-checked list of
  // TH pp.115-117, each rule's reading and its corpus count: docs/INDICES-TH115-117.md.
  TH_IX6_GIAP_THUONG_SU: { side: 'limit', w: 1 }, TH_IX6_CANH_THUONG_SU: { side: 'limit', w: 1 }, TH_IX9_THAN_THUONG: { side: 'limit', w: 1 },
  TH_IX10_TU_MO_KINH_DA_PHAT: { side: 'support', w: 1 }, TH_6N_SPT_TANG_HO: { side: 'limit', w: 1 },
  // the rules of TH pp.115-117 that name death, prison, injury, illness, burns, drowning or mourning (owner's decision 2026-10-24: added,
  // told only as "theo sách rất bất lợi"). TH_6I / TH_6J are the tiểu hạn's only, TH_IX7 needs đại and tiểu hạn on one palace (VAN_HAN).
  TH_IX7_TRUNG_PHUNG_TY: { side: 'limit', w: 1 }, TH_IX8_THUONG_SU_TUE: { side: 'limit', w: 1 }, TH_IX11_SAT_HAM_HINH_HO: { side: 'limit', w: 1 },
  TH_DC5_PHOI: { side: 'limit', w: 1 }, TH_6A_CNDL_SAT: { side: 'limit', w: 1 }, TH_6B_SPLT_KHONG: { side: 'limit', w: 1 },
  TH_6D_CU_CO_DONG_LUONG: { side: 'limit', w: 1 }, TH_6F_NHAT_NGUYET: { side: 'limit', w: 1 }, TH_6G_PHA_LIEM_THAM: { side: 'limit', w: 1 },
  TH_6H_THIEN_DONG: { side: 'limit', w: 1 }, TH_6I_TANG_HOA_LINH: { side: 'limit', w: 1 }, TH_6J_CO_LUONG_THIN_TUAT: { side: 'limit', w: 1 },
  TH_6K_SPLT_TANG_HO: { side: 'limit', w: 1 }, TH_6L_KINH_KHONG_PHUC_BINH: { side: 'limit', w: 1 }, TH_6M_THAM_LIEM_VU: { side: 'limit', w: 1 },
  TH_6O_THAM_LIEM_KY_KIEP: { side: 'limit', w: 1 }, TH_7A_NHAT_NGUYET_DA: { side: 'limit', w: 1 }, TH_7B_PHU_TUONG_CO_QUA: { side: 'limit', w: 1 },
  TH_7C_PHU_TUONG_TANG_HO: { side: 'limit', w: 1 }, TH_7D_SPLT_HAO_TANG: { side: 'limit', w: 1 }, TH_7E_CO_QUA_DAO_HONG: { side: 'limit', w: 1 },
  TH_7F_TPVT_CO_QUA_HAO: { side: 'limit', w: 1 }, TH_7G_KHONG_TANG_HO: { side: 'limit', w: 1 }, TH_7H_HINH_KINH_TANG: { side: 'limit', w: 1 },
  TH_7I_CNDL_TANG_HO: { side: 'limit', w: 1 },
};
/** The kind of hạn a vận sentence is for (the reading's `han`, from van_han_rules.json): 'tieu' = the tiểu hạn only; 'trung_phung' = the
 *  year whose tiểu hạn stands on its đại hạn palace. A sentence without one reads on every hạn palace. */
type Han = 'dai' | 'tieu' | 'trung_phung';
const hanFits = (rule: string | undefined, han: Han) => !rule || (rule === 'tieu' ? han !== 'dai' : han === 'trung_phung');
/** Vận sentences whose page names no side: told in the reading, never scored. */
export const VAN_NO_SIDE: ReadonlySet<string> = new Set(['TH_IX10_TU_MO_KINH_DA']);
export const TRIAD_RULES: ReadonlySet<string> = new Set(['VH_THAI_TUE', 'VH_QUAN_PHU', 'VH_BACH_HO']);
/** Toàn Thư pp.97-105 nhập hạn ca (engine/tvbt/van_han_tt.py): matched by the start of the sentence; the longer prefix is tried first. */
export const TT_SENTENCES: Array<{ id: string; prefix: string; side: Side; w: number }> = [
  ['TT_HAN_TU_VI_SPT', 'Tử Vi nhập hạn nhưng tam phương có Thất Sát', 'limit', 1], ['TT_HAN_TU_VI', 'Hạn đến Tử Vi ở thế đẹp', 'support', 1],
  ['TT_HAN_CO_HOA', 'Hạn Thiên Cơ gặp Khoa, Quyền hoặc Lộc', 'support', 1], ['TT_HAN_CO', 'Hạn Thiên Cơ:', 'limit', 1],
  ['TT_HAN_NHAT_DAC', 'Hạn Thái Dương đắc địa', 'support', 1], ['TT_HAN_NHAT_HAM', 'Hạn Thái Dương hãm địa', 'limit', 1],
  ['TT_HAN_VU_MIEU', 'Hạn Vũ Khúc nhập miếu', 'support', 1], ['TT_HAN_VU_QUYEN', 'Hạn Vũ Khúc có Hóa Quyền', 'support', 1],
  ['TT_HAN_VU_HAM', 'Hạn Vũ Khúc hãm địa', 'limit', 1], ['TT_HAN_DONG_DAC', 'Hạn Thiên Đồng đắc địa', 'support', 1],
  ['TT_HAN_DONG_HAM', 'Hạn Thiên Đồng hãm địa', 'limit', 1], ['TT_HAN_LIEM_VUONG', 'Hạn Liêm Trinh ở thế vượng', 'support', 1],
  ['TT_HAN_PHU', 'Hạn Thiên Phủ:', 'support', 1], ['TT_HAN_NGUYET_HAM', 'Hạn Thái Âm hãm địa', 'limit', 1], ['TT_HAN_NGUYET', 'Hạn Thái Âm:', 'support', 1],
  ['TT_HAN_THAM_MIEU', 'Hạn Tham Lang miếu vượng', 'support', 1], ['TT_HAN_THAM_HOA', 'Hạn Tham Lang ở Tứ mộ gặp Hỏa Tinh', 'support', 1],
  ['TT_HAN_THAM_HAM', 'Hạn Tham Lang hãm địa', 'limit', 1], ['TT_HAN_PHA_MIEU', 'Hạn Phá Quân miếu địa', 'support', 1],
  ['TT_HAN_PHA_SAT', 'Hạn Phá Quân gặp sát tinh', 'limit', 1], ['TT_HAN_PHA_HAM', 'Hạn Phá Quân hãm địa', 'limit', 1],
  ['TT_HAN_LOC_TON', 'Hạn Lộc Tồn:', 'support', 1], ['TT_HAN_KINH_TU_MO', 'Hạn Kình Dương ở Tứ mộ', 'support', 0.5],
  ['TT_HAN_HOA_TINH_DAC', 'Hạn Hỏa Tinh đắc địa', 'support', 1], ['TT_HAN_HOA_TINH_HAM', 'Hạn Hỏa Tinh hãm địa', 'limit', 1],
  ['TT_HAN_LINH_THAM', 'Hạn Linh Tinh gặp Tham Lang', 'support', 1], ['TT_HAN_MA', 'Hạn Thiên Mã gặp Tử, Phủ hoặc Lộc Tồn', 'support', 1],
  ['TT_HAN_HOA_LOC', 'Hạn Hóa Lộc:', 'support', 1], ['TT_HAN_HOA_QUYEN', 'Hạn Hóa Quyền:', 'support', 1],
  ['TT_HAN_HOA_KHOA', 'Hạn Hóa Khoa gặp Văn Xương', 'support', 1], ['TT_HAN_KY_SAT', 'Hạn Hóa Kỵ gặp sát tinh', 'limit', 1], ['TT_HAN_KY', 'Hạn Hóa Kỵ:', 'limit', 1],
].map(([id, prefix, side, w]) => ({ id: id as string, prefix: prefix as string, side: side as Side, w: w as number }))
  .sort((a, b) => b.prefix.length - a.prefix.length);
/** Toàn Thư nhập hạn ca is a paraphrase whose pages are still to be checked: low weight. */
export const TT_WEIGHT = 0.5;
/** Khảo Luận pp.230-233: the tam hợp element of the vận against the birth year's (analysis.age_vs_dai_van). "cùng hành" reads "thoải mái,
 *  mức trung bình": no side, so it adds nothing. */
export const KL_RELATION: Record<string, { id: string; side: Side; w: number }> = {
  'đại vận sinh nhập cho tuổi': { id: 'KL_DV_SINH_NHAP', side: 'support', w: 1 },
  'tuổi khắc đại vận': { id: 'KL_DV_TUOI_KHAC_VAN', side: 'support', w: 0.6 },
  'tuổi sinh xuất cho đại vận': { id: 'KL_DV_SINH_XUAT', side: 'limit', w: 0.6 },
  'đại vận khắc tuổi': { id: 'KL_DV_VAN_KHAC_TUOI', side: 'limit', w: 1 },
};
const HOA_ID: Record<string, string> = { 'Hóa Lộc': 'LOC', 'Hóa Quyền': 'QUYEN', 'Hóa Khoa': 'KHOA', 'Hóa Kỵ': 'KY' };
const DV_HOA_CITE = 'thông lệ (Tứ Hóa theo can đại vận, phép phi hóa); ba sách không có câu luận cho lớp này';
const LUU_HOA_CITE = 'thông lệ, chưa có trong ba sách (KL tr.41-42, TH tr.114 liệt kê chín sao lưu, không có Tứ Hóa)';
const LUU_POS_CITE = 'vị trí: KL tr.41-42 (cùng chín sao ở TH tr.114)';


// ---- KL p.233 mục 3-4: the stars of a vận palace read by their brightness ----
// "Xem đến các chính tinh cung đại vận và các cung nhị, tam hợp, xung chiếu. Chính tinh đắc địa thì tốt, hãm địa thì xấu, hãm địa phải có
// Tuần Triệt giải mới tốt. Trung tinh đắc địa thì tốt, hãm địa thì xấu. Hung tinh đắc địa thì tốt, gặp đúng quan thầy trong bộ Sát Phá Tham
// càng tốt hơn, thí dụ Không Kiếp gặp Phá quân, Hỏa Linh gặp Tham lang, Kình Đà gặp Thất sát. Hung tinh hãm địa thì xấu lắm." (KL p.233)
/** Trung tinh: the stars other than the fourteen in KL p.36's table "các tên chính tinh và trung tinh dùng trong Tứ hóa" (page image). */
export const TRUNG_TINH: readonly string[] = ['Văn Xương', 'Văn Khúc', 'Tả Phụ', 'Hữu Bật'];
/** Hung tinh: the six KL p.233 pairs with their quan thầy in the same sentence. */
export const QUAN_THAY: Record<string, string> = { 'Địa Không': 'Phá Quân', 'Địa Kiếp': 'Phá Quân', 'Hỏa Tinh': 'Tham Lang', 'Linh Tinh': 'Tham Lang',
  'Kình Dương': 'Thất Sát', 'Đà La': 'Thất Sát' };
export const HUNG_TINH: readonly string[] = Object.keys(QUAN_THAY);
type StarClass = 'chinh' | 'trung' | 'hung';
const CLASS_VI: Record<StarClass, string> = { chinh: 'chính tinh', trung: 'trung tinh', hung: 'hung tinh' };
/** "đắc địa": the printed levels miếu, vượng, đắc; "hãm địa": hãm. bình and lợi are neither, so they add nothing. */
const DAC = new Set(['miếu', 'vượng', 'đắc']);
/** Weights inside the vận layer (system convention): one star's brightness counts half a book sentence about the vận; a trung tinh half a
 *  chính tinh; "Hung tinh hãm địa thì xấu lắm" and "càng tốt hơn" with its quan thầy ×1.5. */
export const DH_K = 0.5;
export const DH_CLASS_W: Record<StarClass, number> = { chinh: 1, trung: 0.5, hung: 1 };
export const DH_STRONG = 1.5;
const KL233 = 'KL tr.233 mục 4';

// ---- TH p.115 IX.1-4: Nam đẩu and Bắc đẩu tinh in the hạn ----
// "1. Dương nam, Âm nữ hạn gặp được Nam đẩu tinh thì tốt. 2. Âm nam, Dương nữ hạn gặp được Bắc đẩu tinh thì tốt. 3. Bắc đẩu ứng tốt xấu mạnh
// ở 5 năm về trước của Đại hạn; 4. Nam đẩu ứng tốt xấu mạnh ở 5 năm về sau của Đại hạn" (TH p.115, page image). Which star is which: the
// heading of each star in TH (page images, 2026-10-24); Tử Vi "Nam bắc đẩu" is both; Thiên Mã, Địa Không, Địa Kiếp carry no tag.
export const DAU_TINH: Record<string, { group: 'nam' | 'bac' | 'ca_hai'; page: number }> = {
  'Tử Vi': { group: 'ca_hai', page: 29 }, 'Thiên Cơ': { group: 'nam', page: 30 }, 'Thái Dương': { group: 'nam', page: 31 }, 'Vũ Khúc': { group: 'bac', page: 33 },
  'Thiên Đồng': { group: 'nam', page: 35 }, 'Liêm Trinh': { group: 'bac', page: 36 }, 'Thiên Phủ': { group: 'nam', page: 37 }, 'Thái Âm': { group: 'bac', page: 39 },
  'Tham Lang': { group: 'bac', page: 40 }, 'Cự Môn': { group: 'bac', page: 42 }, 'Thiên Tướng': { group: 'nam', page: 44 }, 'Thiên Lương': { group: 'nam', page: 45 },
  'Thất Sát': { group: 'nam', page: 46 }, 'Phá Quân': { group: 'bac', page: 47 }, 'Thiên Khôi': { group: 'nam', page: 49 }, 'Thiên Việt': { group: 'nam', page: 49 },
  'Văn Xương': { group: 'bac', page: 50 }, 'Văn Khúc': { group: 'nam', page: 50 }, 'Tả Phụ': { group: 'bac', page: 51 }, 'Hữu Bật': { group: 'bac', page: 51 },
  'Lộc Tồn': { group: 'bac', page: 51 }, 'Kình Dương': { group: 'bac', page: 62 }, 'Đà La': { group: 'bac', page: 63 }, 'Hỏa Tinh': { group: 'nam', page: 64 },
  'Linh Tinh': { group: 'nam', page: 64 },
};
const DAU_VI = { nam: 'Nam đẩu', bac: 'Bắc đẩu' } as const;

// ---- weights of the period layers (system convention; each layer is scaled to its typical size first, so the weights compare like with like) ----
// Book evidence decides the direction (owner rule 2026-10-21: a convention never overrules a book sentence): the sourced layers carry most of
// the weight, and the convention layers (CONVENTION) only modulate — their sum is capped at CONV_K × |sourced part| (+ CONV_FLOOR when they
// point the same way or the books are silent), so they can strengthen or soften the books' direction but never flip it.
export const W_DECADE = { van: 0.8, hoa_van: 0.2 } as const;
export const W_YEAR = { dai_van: 0.3, dau_tinh: 0.1, tieu_han: 0.3, luu_dai_han: 0.15, luu_sao: 0.07, luu_sao_tl: 0.03, luu_tu_hoa: 0.05 } as const;
export const CONVENTION: ReadonlySet<Layer> = new Set<Layer>(['hoa_van', 'luu_tu_hoa', 'luu_sao_tl']);
export const CONV_K = 0.5, CONV_FLOOR = 0.15;
export const W_MONTH = 0.25;
/** TH p.118 calls a Mệnh "sáng sủa" or "hắc ám"; where that line falls is a system convention: Mệnh's natal net (radar support − limit) and
 *  the Thân palace's, at least MENH_Z typical sizes above (below) the typical chart. */
export const MENH_Z = 0.75;
/** The five levels: the corpus quantiles 12 / 33 / 67 / 88 % of the scores of each kind of period with book evidence (system convention).
 *  A level is a comparison with the periods of the 1,000 sample charts, not the books' direction alone: the book material read here leans
 *  favourable (the brightness tables print more đắc than hãm places, most vận sentences are good ones), so a scale anchored at 0 put 99.6 %
 *  of the corpus decades at "Thuận" or above (tried 2026-10-24). When a level and the books' side disagree, the words say so. */
export const LEVELS = ['Rất thử thách', 'Nhiều thử thách', 'Trung bình', 'Thuận', 'Rất thuận'] as const;
export const LEVEL_Q = [0.12, 0.33, 0.67, 0.88];
/** The level told for a period with no book item: the middle, flagged — not a real middle (owner's decision 2026-10-24). */
export const LEVEL_DEFAULT = 2;
export const INSUFFICIENT_VI = 'chưa đủ căn cứ';
const FALLBACK_CUTS = [-1.175, -0.44, 0.44, 1.175];   // the same quantiles of a unit normal, when no corpus norms are loaded

/** Corpus norms (engine/data/kg/index_norms.json, tools/interpret/index_norms.ts). */
export interface LayerNorm { mean: number; sd: number; rms: number }
export interface IndexNorms {
  version: string; kbVersion: string; charts: number; corpus: string;
  /** mean raw natal sums per palace name (the radar) */
  palace: Record<string, { support: number; limit: number }>;
  /** mean, spread and root mean square of every period layer's raw net value (the rms is the unit: raw / rms, not centred) */
  layers?: Record<string, LayerNorm>;
  /** level cut points per kind of period (LEVEL_Q quantiles of the scores of the periods with book evidence) */
  cuts?: { decade: number[]; year: number[]; month: number[] };
}

// ================================================================ natal (radar) ================================================================

/** Verified natal findings per palace, each weighed by its seat tier (with its own palace as centre) and rarity on that palace. */
function natalItems(chart: ChartInput, k: Knowledge): Map<string, Item[]> {
  const rmap = new Map<string, Rule>(k.rules.map(r => [r.id, r]));
  const guards = new Map((k.kg?.positionGuards ?? []).map(g => [g.ruleId, g]));
  const world: World = n => chart.base[`palace:${n}`] ? { ...(chart.base.chart ?? {}), ...chart.base[`palace:${n}`] } : null;
  const geo = new Map<string, Geo>();
  const out = new Map<string, Item[]>(chart.palaces.map(p => [p.name, []]));
  const seen = new Map<string, Item>();
  for (const f of run(k.rules, k.sources, chart.base).findings) {
    if (f.basis !== 'verified' || f.effect === 'neutral' || !f.palace || !out.has(f.palace)) continue;
    const rule = rmap.get(f.ruleId)!;
    const atoms = triggerAtoms(rule.conditions, { ...(chart.base.chart ?? {}), ...(chart.base[f.subject] ?? {}) }, world, f.palace);
    const gd = guards.get(f.ruleId);
    if (gd && !guardHolds(gd, atoms, chart.palaces, { here: f.palace, tuHoa: chart.tu_hoa })) continue;
    const g = geo.get(f.palace) ?? geo.set(f.palace, new Geo(chart, f.palace)).get(f.palace)!;
    const tiers = atoms.map(a => atomSeat(a, g)).filter(s => s && s.kind !== 'degree').map(s => s!.tier);
    const tier = (tiers.length ? Math.min(...tiers) : 5) as Tier;
    // rarity on the palace the finding stands on (kg.baseRates.palaces), not on Mệnh
    const w = r3(TIER_WEIGHT[tier] * (0.5 + rarity(k, f.ruleId, f.palace)));
    // the same claim on the same palace (two books, two rules) counts once, at its strongest
    const key = `${f.palace}|${f.claim}|${f.effect}`, prev = seen.get(key);
    if (prev) { if (w > prev.w) Object.assign(prev, { id: f.ruleId, w, cite: rule.cites.join('; ') }); continue; }
    const item: Item = { id: f.ruleId, side: f.effect, w, layer: 'ban_menh', palace: f.palace, scope: 'self', cite: rule.cites.join('; '),
      text: (k.claims[f.claim] ?? rule.reading ?? f.claim).trim(), basis: 'sach' };
    seen.set(key, item);
    out.get(f.palace)!.push(item);
  }
  for (const xs of out.values()) xs.sort((a, b) => b.w - a.w || (a.id < b.id ? -1 : 1));
  return out;
}

type Ctx = { chart: ChartInput; byName: Map<string, Palace>; byBranch: Map<string, Palace>; byIndex: Map<number, Palace>; natal: Map<string, Item[]> };
function context(chart: ChartInput, k: Knowledge): Ctx {
  return { chart, byName: new Map(chart.palaces.map(p => [p.name, p])), byBranch: new Map(chart.palaces.map(p => [p.branch, p])),
    byIndex: new Map(chart.palaces.map(p => [p.branch_index, p])), natal: natalItems(chart, k) };
}

/** The palace, its opposite and its two tam hợp, with the relation of each to the palace. */
function tamPhuong(c: Ctx, name: string): Array<{ p: Palace; rel: 'self' | 'opp' | 'trine' }> {
  const t = c.byName.get(name)!;
  return c.chart.palaces.map(p => ({ p, rel: REL_OF[(p.branch_index - t.branch_index + 12) % 12] })).filter(x => x.rel)
    .sort((a, b) => ['self', 'opp', 'trine'].indexOf(a.rel) - ['self', 'opp', 'trine'].indexOf(b.rel) || a.p.branch_index - b.p.branch_index);
}
/** Where a palace stands from a period palace: in its tam phương, else Mệnh, else out of reach. */
function reach(c: Ctx, from: string, to: string | null | undefined): Rel | null {
  if (!to) return null;
  const r = tamPhuong(c, from).find(x => x.p.name === to)?.rel;
  return r ?? (to === 'Mệnh' ? 'menh' : null);
}

const sum = (xs: Item[], side: Side) => r3(xs.filter(x => x.side === side).reduce((a, x) => a + x.w, 0));
const net = (xs: Item[]) => r3(sum(xs, 'support') - sum(xs, 'limit'));

/** Raw natal sums of a palace: its own verified findings and those of its tam phương, scope-weighted (what the corpus norms average). */
function natalRaw(c: Ctx, name: string): { support: number; limit: number; items: Item[] } {
  const items = tamPhuong(c, name).flatMap(({ p, rel }) => (c.natal.get(p.name) ?? []).map(x => ({ ...x, scope: rel, w: r3(x.w * SCOPE_WEIGHT[rel]) })));
  return { support: sum(items, 'support'), limit: sum(items, 'limit'), items };
}
/** Smoothing of the radar ratio: one plain finding rounded up. */
export const NORM_SMOOTH = 1;
export interface PalaceIndex { palace: string; branch: string; support: number; limit: number; note: string; items: Item[] }
/** Natal quality of a palace as a ratio to the corpus mean of the same palace: (sum + 1) / (mean + 1); 1 = the typical chart there. */
function natalIndex(c: Ctx, name: string, norms: IndexNorms | null): PalaceIndex {
  const r = natalRaw(c, name), n = norms?.palace[name];
  const ratio = (x: number, m: number | undefined) => m === undefined ? r3(x) : r3((x + NORM_SMOOTH) / (m + NORM_SMOOTH));
  const note = n ? `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} so với trung bình ${vn(n.support)} / ${vn(n.limit)} của ${norms!.charts.toLocaleString('vi-VN')} lá số mẫu`
    : `cung ${name} và tam phương: tổng ${vn(r.support)} / ${vn(r.limit)} (chưa có mức trung bình để so)`;
  return { palace: name, branch: c.byName.get(name)!.branch, support: ratio(r.support, n?.support), limit: ratio(r.limit, n?.limit), note, items: r.items };
}

/** Raw natal sums of all twelve palaces of a chart (input of tools/interpret/index_norms.ts). */
export function natalRawAll(chart: ChartInput, k: Knowledge): Record<string, { support: number; limit: number }> {
  const c = context(chart, k);
  return Object.fromEntries(chart.palaces.map(p => { const r = natalRaw(c, p.name); return [p.name, { support: r.support, limit: r.limit }]; }));
}

// ================================================================ period items ================================================================

const bookOf = (cite: string) => /Khảo Luận|KL /.test(cite) ? 'Khảo Luận' : /Thực Hành|TH /.test(cite) ? 'Thực Hành' : /Toàn Thư|TT /.test(cite) ? 'Toàn Thư' : /Hàm Số|HS /.test(cite) ? 'Hàm Số' : undefined;
const LOWER_LEAD = /^(Cung|Vận|Hạn|Tam|Lưu)\b/;
const lowerLead = (s: string) => LOWER_LEAD.test(s) ? s[0].toLowerCase() + s.slice(1) : s;
/** "Vận có Tham Lang ở Dậu: theo sách hao tài, phóng túng." → "vận có Tham Lang ở Dậu thì hao tài, phóng túng". */
export function gistOf(text: string): string {
  const t = text.trim().replace(/\.\s*$/, '').split('; ')[0];
  const i = t.indexOf(': ');
  if (i < 0) return lowerLead(t);
  const cond = t.slice(0, i), rest = t.slice(i + 2).replace(/^(theo sách|sách xem|sách đọc là|sách cho là)\s+/, '');
  const glue = /^(là|đây|đó|cung vận này|cung vận có)\b/.test(rest) ? ', ' : ' thì ';
  return `${lowerLead(cond)}${glue}${rest.replace(/^là /, 'đó là ')}`;
}

type DecadeFacts = ChartInput['decades'][number] & { tt?: Array<{ text: string; src: string }>;
  kl?: { src: string; relation: string; verdict: string; xung_controlled: boolean; event?: string | null; thai_tue_triad?: boolean;
    nhi_hop?: { branch: string; palace: string; counts: boolean; majors: string[] } } | null };

/** The book sentences of a vận palace (đại hạn, tiểu hạn, lưu đại hạn): rule-id readings, Toàn Thư paraphrases, Khảo Luận pp.230-233 facts.
 *  `where` is added to each cite when the palace is placed by another page (the lưu đại hạn of TH pp.117-118). */
function vanItems(palace: string, layer: Layer, readings: DecadeFacts['readings'], tt: ReturnType<typeof toanThuLines>, kl: DecadeFacts['kl'], where = '', han: Han = 'dai'): Item[] {
  const list: Item[] = [];
  const add = (it: Omit<Item, 'layer' | 'palace' | 'scope' | 'book'>) => list.push({ ...it, cite: it.cite + where, w: r3(it.w), layer, palace, scope: 'self', book: bookOf(it.cite) });
  for (const r of readings as Array<{ text: string; src: string; rule_id?: string | null; han?: string }>) {
    const t = r.rule_id && hanFits(r.han, han) ? VAN_RULES[r.rule_id] : undefined;
    if (t) add({ id: r.rule_id!, side: t.side, w: t.w, cite: TRIAD_RULES.has(r.rule_id!) ? `${r.src}; KL tr.233 (tam hợp Thái Tuế, Quan Phù, Bạch Hổ: “bất kể Mệnh đóng ở vị trí nào”)` : r.src,
      text: r.text, basis: 'sach', gist: gistOf(r.text) });
  }
  // Toàn Thư's nhập hạn verses, page-checked (prose/vanhan_books.ts, the lines the đại hạn chapter voices; review of the live charts
  // 2026-10-25: the older paraphrases cited "chưa đối chiếu" while the prose cited the page). Weight TT_WEIGHT each, as before.
  for (const b of tt) if (b.tone) add({ id: `TT_HAN:${b.id.replace(/^TT_HAN:/, '')}`, side: b.tone === 'pos' ? 'support' : 'limit', w: TT_WEIGHT, cite: `Toàn Thư ${b.cite.replace(/^TT /, '')}`,
    text: b.text, basis: 'sach', gist: gistOf(b.text) });
  if (kl) {
    const t = KL_RELATION[kl.relation];
    if (t) add({ id: t.id, side: t.side, w: t.w, cite: kl.src, basis: 'sach',
      text: `Tam hợp của cung vận so với tuổi: ${kl.relation}, sách đọc là ${kl.verdict}.`,
      gist: `hành tam hợp của cung vận và của tuổi ở thế “${kl.relation}”, sách đọc là ${kl.verdict}` });
    if (kl.xung_controlled) add({ id: 'KL_DV_KHAC_XUNG', side: 'support', w: 0.5, cite: kl.src, basis: 'sach',
      text: 'Tam hợp cung vận khắc tam hợp cung xung chiếu: theo sách nhận sao tốt, từ chối sao xấu của cung xung chiếu.',
      gist: 'tam hợp cung vận khắc tam hợp cung xung chiếu, nên nhận sao tốt và từ chối sao xấu của cung ấy' });
    // the Thái Tuế – Quan Phù – Bạch Hổ triad of KL p.233 is the same condition as VH_THAI_TUE / VH_QUAN_PHU / VH_BACH_HO above: not counted twice
  }
  return list;
}

const classOf = (p: Palace, star: string): StarClass | null =>
  p.major_stars.includes(star) ? 'chinh' : TRUNG_TINH.includes(star) ? 'trung' : HUNG_TINH.includes(star) ? 'hung' : null;
/** A star's brightness when it is page-checked (dignity_status VERIFIED, with its page); unverified or disputed levels are not read. */
function brightness(p: Palace, star: string): { value: string; locator: string } | null {
  const s = p.dignity_status?.[star];
  return s?.status === 'VERIFIED' && s.value ? { value: s.value, locator: s.locator ?? '' } : null;
}
/** KL p.233 mục 3-4 on a vận palace: the chính, trung and hung tinh of the palace, its xung chiếu and tam hợp, and its nhị hợp when the
 *  nhị hợp generates the vận (mục 3; đại hạn only: `kl.nhi_hop.counts`). With `kl.xung_controlled` (KL p.232) the vận "từ chối sao xấu của
 *  cung xung chiếu": the hãm stars of the opposite palace are not counted. `what` names the palace's role in the words. */
const KINH_DA = new Set(['Kình Dương', 'Đà La']), TU_MO = new Set(['Thìn', 'Tuất', 'Sửu', 'Mùi']);
/** "lưỡng hạn" of TH p.115 IX.10: the đại hạn (and its lưu đại hạn) and the tiểu hạn, not the nguyệt hạn. */
const IX10_LAYERS: ReadonlySet<Layer> = new Set<Layer>(['van', 'tieu_han', 'luu_dai_han']);
function dhItems(c: Ctx, at: string, layer: Layer, kl: DecadeFacts['kl'] | null, what: string, where = ''): Item[] {
  const seats: Array<{ p: Palace; rel: Rel }> = tamPhuong(c, at);
  const nh = kl?.nhi_hop?.counts ? c.byName.get(kl.nhi_hop.palace) : undefined;
  if (nh && !seats.some(x => x.p.name === nh.name)) seats.push({ p: nh, rel: 'nhi_hop' });
  const out: Item[] = [];
  for (const { p, rel } of seats) for (const star of p.stars) {
    const cls = classOf(p, star), b = cls && brightness(p, star);
    if (!cls || !b) continue;
    const good = DAC.has(b.value), bad = b.value === 'hãm';
    if (!good && !bad) continue;
    if (bad && rel === 'opp' && kl?.xung_controlled) continue;
    const giai = bad && cls === 'chinh' && (p.tuan || p.triet), qt = good && cls === 'hung' && p.stars.includes(QUAN_THAY[star]);
    const id = giai ? 'KL233_HAM_GIAI' : qt ? 'KL233_HUNG_QUAN_THAY' : good ? 'KL233_DAC' : 'KL233_HAM';
    const w = DH_K * DH_CLASS_W[cls] * REL_W[rel] * (qt || (bad && cls === 'hung') ? DH_STRONG : 1);
    const reading = giai ? `chính tinh hãm địa có ${p.tuan ? 'Tuần' : 'Triệt'} giải thì tốt` : qt ? `hung tinh đắc địa gặp quan thầy ${QUAN_THAY[star]} càng tốt`
      : `${CLASS_VI[cls]} ${good ? 'đắc địa thì tốt' : cls === 'hung' ? 'hãm địa thì xấu lắm' : 'hãm địa thì xấu'}`;
    out.push({ id, side: giai || good ? 'support' : 'limit', w: r3(w), layer, palace: p.name, scope: rel, basis: 'sach', book: 'Khảo Luận', star, dignity: b.value,
      cite: `${KL233}${rel === 'nhi_hop' ? ' và mục 3 (cung nhị hợp sinh xuất cho cung vận)' : ''}; độ sáng: ${b.locator}${where}`,
      text: `${star} ${b.value} ở ${p.branch} (cung ${p.name}${rel === 'self' ? `, chính cung ${what}` : `, ${REL_VI[rel]} của cung ${what}`}): ${reading}.` });
    if (bad && rel === 'self' && KINH_DA.has(star) && IX10_LAYERS.has(layer) && TU_MO.has(c.chart.year_gz?.split(' ')[1] ?? ''))
      // TH p.115 IX.10 "Người tuổi Thìn, Tuất, Sửu, Mùi mà lưỡng hạn gặp Kình, Đà, không hề gì" (owner 2026-10-24: it cancels the KL p.233 hãm):
      // the hãm stays in the list and this item takes it back, so both books are told. KL233_ prefix: it follows the hãm into the đẩu tinh layer.
      out.push({ id: 'KL233_HAM_TH115_IX10', side: 'support', w: r3(w), layer, palace: p.name, scope: rel, basis: 'sach', book: 'Thực Hành', star, dignity: b.value,
        cite: `TH tr.115 mục IX.10 (người tuổi Thìn, Tuất, Sửu, Mùi mà lưỡng hạn gặp Kình, Đà, không hề gì), bù phần hãm của ${KL233}; độ sáng: ${b.locator}${where}`,
        text: `${star} ${b.value} ở ${p.branch} (chính cung ${what}): tuổi ${c.chart.year_gz.split(' ')[1]} gặp Kình, Đà thì Thực Hành nói không hề gì, nên phần hãm địa được bù lại.` });
  }
  return out.sort((a, b) => b.w - a.w || (a.star! < b.star! ? -1 : 1));
}

/** The direction a hạn's Nam / Bắc đẩu favour: TH p.115 IX.1-2 by âm dương of the person. */
const dauFor = (chart: ChartInput): 'nam' | 'bac' => chart.yin_yang_gender === 'dương nam' || chart.yin_yang_gender === 'âm nữ' ? 'nam' : 'bac';
const dauOf = (star: string) => DAU_TINH[star]?.group;
/** TH p.115 IX.1-2: the Nam (or Bắc) đẩu chính tinh of the hạn palace itself are good for this person. One sentence, its stars named. */
function dauItems(chart: ChartInput, p: Palace, layer: Layer, what: string, where = ''): Item[] {
  // the chính tinh of the hạn palace (how the system reads "hạn gặp": the stars that make the palace; the minor ones would fire on nearly every palace)
  const g = dauFor(chart), stars = p.major_stars.filter(s => dauOf(s) === g || dauOf(s) === 'ca_hai');
  if (!stars.length) return [];
  const people = g === 'nam' ? 'dương nam, âm nữ' : 'âm nam, dương nữ';
  return [{ id: g === 'nam' ? 'TH115_NAM_DAU' : 'TH115_BAC_DAU', side: 'support', w: 1, layer, palace: p.name, scope: 'self', basis: 'sach', book: 'Thực Hành',
    cite: `TH tr.115 mục IX.${g === 'nam' ? 1 : 2} (xét chính tinh của cung hạn: cách hiểu của hệ thống); sao ${DAU_VI[g]}: ${stars.map(s => `${s} TH tr.${DAU_TINH[s].page}`).join(', ')}${where}`,
    text: `Cung ${what} có ${stars.join(', ')} (${DAU_VI[g]}${stars.some(s => dauOf(s) === 'ca_hai') ? '; Tử Vi là cả Nam lẫn Bắc đẩu' : ''}): Thực Hành viết người ${people} hạn gặp ${DAU_VI[g]} tinh thì tốt.`,
    gist: `cung ${what} có ${stars.join(', ')} là ${DAU_VI[g]} tinh, hợp với người ${people}` }];
}

/** Tứ Hóa of a stem landing within reach of a period palace (its tam phương or Mệnh). */
function hoaItems(c: Ctx, hoa: ChartInput['decades'][number]['hoa'] | undefined, at: string, layer: 'hoa_van' | 'luu_tu_hoa', stem: string, scale = 1): Item[] {
  const out: Item[] = [];
  for (const [h, v] of Object.entries(hoa ?? {})) {
    const rel = reach(c, at, v.palace);
    if (!rel) continue;
    const id = `${layer === 'hoa_van' ? 'DV' : 'LUU'}_HOA_${HOA_ID[h] ?? h}`;
    out.push({ id, side: h === 'Hóa Kỵ' ? 'limit' : 'support', w: r3(REL_W[rel] * scale), layer, palace: v.palace!, scope: rel, basis: 'thong_le',
      cite: layer === 'hoa_van' ? DV_HOA_CITE : LUU_HOA_CITE,
      text: `${h} của can ${stem} (trên ${v.star}) vào cung ${v.palace}${rel === 'menh' ? '' : `, ${REL_VI[rel]} của cung ${layer === 'hoa_van' ? 'đại vận' : 'tiểu hạn'}`}.` });
  }
  return out;
}
const REL_VI: Record<Rel, string> = { self: 'chính cung', opp: 'xung chiếu', trine: 'tam hợp', nhi_hop: 'nhị hợp', menh: 'Mệnh' };

// ---- where the year's palaces stand ----
/** Age 1 of the tiểu hạn by the birth-year triad (TH p.27, KL pp.39-40 agree): Dần Ngọ Tuất → Thìn, Thân Tý Thìn → Tuất, Tỵ Dậu Sửu → Mùi,
 *  Hợi Mão Mùi → Sửu. */
const TH_START: Record<number, number> = { 2: 4, 6: 4, 10: 4, 8: 10, 0: 10, 4: 10, 5: 7, 9: 7, 1: 7, 11: 1, 3: 1, 7: 1 };
const mod12 = (x: number) => ((x % 12) + 12) % 12;
/** The tiểu hạn branch at a tuổi mụ: KL pp.39-40 dương nam / âm nữ thuận, âm nam / dương nữ nghịch; TH p.27 nam thuận, nữ nghịch. */
export function tieuHanBranch(chart: ChartInput, age: number, rule: 'KL' | 'TH'): number {
  const yb = BRANCHES.indexOf(chart.year_gz.split(' ')[1]);
  const fwd = rule === 'KL' ? chart.yin_yang_gender === 'dương nam' || chart.yin_yang_gender === 'âm nữ' : /nam$/i.test(chart.yin_yang_gender);
  return mod12(TH_START[yb] + (age - 1) * (fwd ? 1 : -1));
}
/** The chart's tiểu hạn school: facts.tieu_han_rule, or for older facts the one that puts the viewed year where the engine put it. */
export function tieuHanRule(chart: ChartInput): 'KL' | 'TH' {
  if (chart.tieu_han_rule === 'KL' || chart.tieu_han_rule === 'TH') return chart.tieu_han_rule;
  const b = BRANCHES.indexOf(chart.year.tieu_han_branch ?? ''), age = chart.year.year - chart.lunar_year + 1;
  return b >= 0 && tieuHanBranch(chart, age, 'KL') !== b && tieuHanBranch(chart, age, 'TH') === b ? 'TH' : 'KL';
}
/** TH pp.117-118, lưu đại hạn: the first year of a decade at the decade palace, the second at its opposite, the third one palace on from the
 *  opposite against the đại hạn direction, the fourth at the opposite again, then from the opposite a palace a year with the đại hạn
 *  direction. The book's example (dương nữ, nghịch; decade at Tử = Hợi from 32): 33 Điền (Tỵ), 34 Quan (Ngọ), 35 Điền, 36 Phúc (Thìn),
 *  37 Phụ (Mão), 38 Mệnh (Dần), 39 Bào (Sửu). `k` = years since the decade began, `dir` = +1 thuận, −1 nghịch. */
export function luuDaiHanBranch(decadeBranch: number, dir: 1 | -1, k: number): number {
  const opp = decadeBranch + 6;
  return mod12(k === 0 ? decadeBranch : k === 1 || k === 3 ? opp : k === 2 ? opp - dir : opp + (k - 3) * dir);
}

// ---- the nine lưu stars (KL tr.41-42; TH tr.114) for any year: positions from the year stem and branch, as engine/tvbt/reasoning/temporal_facts.luu_tinh ----
const LOC_TON = [2, 3, 5, 6, 5, 6, 8, 9, 11, 0];          // KL tr.42 bảng Lưu Lộc Tồn: Giáp Dần, Ất Mão, Bính/Mậu Tỵ, Đinh/Kỷ Ngọ, Canh Thân, Tân Dậu, Nhâm Hợi, Quý Tý
const MA = [2, 11, 8, 5];                                  // KL tr.42: Thân Tý Thìn → Dần, Tỵ Dậu Sửu → Hợi, Dần Ngọ Tuất → Thân, Hợi Mão Mùi → Tỵ
export function luuStars(chart: ChartInput, year: number): Record<string, string> {
  const ys = (((year - 4) % 10) + 10) % 10, yb = (((year - 4) % 12) + 12) % 12, lt = LOC_TON[ys];
  const fwd = chart.yin_yang_gender === 'dương nam' || chart.yin_yang_gender === 'âm nữ';
  const pos: Record<string, number> = { 'Thái Tuế': yb, 'Tang Môn': yb + 2, 'Bạch Hổ': yb + 8, 'Thiên Khốc': 6 - yb, 'Thiên Hư': 6 + yb,
    'Lộc Tồn': lt, 'Kình Dương': lt + (fwd ? 1 : -1), 'Đà La': lt - (fwd ? 1 : -1), 'Thiên Mã': MA[yb % 4] };
  const byIndex = new Map(chart.palaces.map(p => [p.branch_index, p.name]));
  return Object.fromEntries(Object.entries(pos).map(([k, v]) => [k, byIndex.get(((v % 12) + 12) % 12)!]));
}
/** The side a lưu star takes. Khốc, Hư: TH tr.114 ("gặp hai Khốc, Hư là xấu") at the tiểu hạn itself; elsewhere in reach and for Kình, Đà
 *  (sát tinh) and Lộc Tồn the side of their kind is a convention. Thái Tuế, Tang Môn, Bạch Hổ, Thiên Mã: positions only, no side. */
const LUU_SIDE: Record<string, Side> = { 'Thiên Khốc': 'limit', 'Thiên Hư': 'limit', 'Kình Dương': 'limit', 'Đà La': 'limit', 'Lộc Tồn': 'support' };
const LUU_ID: Record<string, string> = { 'Thiên Khốc': 'LUU_KHOC', 'Thiên Hư': 'LUU_HU', 'Kình Dương': 'LUU_KINH', 'Đà La': 'LUU_DA', 'Lộc Tồn': 'LUU_LOC_TON' };
function luuItems(c: Ctx, th: string, luu: Record<string, string>): Item[] {
  const out: Item[] = [];
  for (const [star, side] of Object.entries(LUU_SIDE)) {
    const at = luu[star], rel = reach(c, th, at);
    if (!rel) continue;
    const book = (star === 'Thiên Khốc' || star === 'Thiên Hư') && rel === 'self';
    out.push({ id: LUU_ID[star], side, w: REL_W[rel], layer: 'luu_sao', palace: at, scope: rel, basis: book ? 'sach' : 'thong_le', book: book ? 'Thực Hành' : undefined,
      cite: book ? `${LUU_POS_CITE}; nghĩa: TH tr.114 (“gặp hai Khốc, Hư là xấu”)` : `${LUU_POS_CITE}; bên ${side === 'limit' ? 'bất lợi' : 'thuận'} theo loại sao: thông lệ`,
      text: `Lưu ${star} ở cung ${at}${rel === 'self' ? ', ngay cung tiểu hạn' : rel === 'menh' ? '' : `, ${REL_VI[rel]} của tiểu hạn`}.` });
  }
  // TH tr.114: Khốc, Hư at the tiểu hạn "nếu có thêm các hung tinh thì ấy là năm đầy tai ương, nước mắt"
  const kh = ['Thiên Khốc', 'Thiên Hư'].filter(s => luu[s] === th);
  const hung = [...['Kình Dương', 'Đà La'].filter(s => luu[s] === th).map(s => `lưu ${s}`), ...SAT.filter(s => c.byName.get(th)!.stars.includes(s))];
  if (kh.length && hung.length) out.push({ id: 'TH_LUU_KHOC_HU_HUNG', side: 'limit', w: 1, layer: 'luu_sao', palace: th, scope: 'self', basis: 'sach', book: 'Thực Hành',
    cite: 'TH tr.114', text: `Lưu ${kh.join(', ')} gặp hung tinh (${hung.join(', ')}) ngay cung tiểu hạn: Thực Hành gọi là năm đầy tai ương, nước mắt.` });
  return out;
}

// ================================================================ period inputs (raw) ================================================================

/** One raw layer of a period: its net value before scaling, and the items behind it. */
export interface RawLayer { layer: Layer; raw: number; items: Item[]; note: string; basis: ItemBasis | 'tinh_toan' }
export interface DecadeRaw { d: DecadeFacts; layers: RawLayer[] }
export interface YearRaw { year: number; age: number; can_chi: string; palace: string; branch: string; thai_tue: string; luu_dai_han: string | null;
  decade: number | null; layers: RawLayer[]; luu: Record<string, string> }
export interface MonthRaw { month: number; palace: string; layer: RawLayer }
export interface PeriodInputs {
  Y0: number;
  /** the tiểu hạn school the years and months were walked with */
  rule: 'KL' | 'TH';
  palaces: PalaceIndex[];                     // radar (needs norms.palace; computed with the norms given)
  natalNet: Record<string, number>;           // radar support − limit per palace
  than: string | null;                        // the Thân palace when it is not Mệnh (TH p.118 reads Mệnh and Thân)
  decades: DecadeRaw[]; years: YearRaw[]; months: MonthRaw[] | null;
}

const SOURCED = (i: Item) => i.basis === 'sach' || i.basis === 'sach_dien_giai';
const countOf = (xs: Item[]) => ({ s: xs.filter(i => !i.id.startsWith('KL233_')).length, d: xs.filter(i => i.id.startsWith('KL233_')).length });
const LDH_CITE = '; vị trí: lưu đại hạn, TH tr.117-118';

export function periodInputs(chart: ChartInput, k: Knowledge, norms: IndexNorms | null, span = 10, opts: { tieuHanRule?: 'KL' | 'TH' } = {}): PeriodInputs {
  const c = context(chart, k);
  const m = c.byName.get('Mệnh')!;
  const palaces = [...chart.palaces].sort((a, b) => (a.branch_index - m.branch_index + 12) % 12 - (b.branch_index - m.branch_index + 12) % 12)
    .map(p => natalIndex(c, p.name, norms));
  const natalNet = Object.fromEntries(palaces.map(p => [p.palace, r3(p.support - p.limit)]));

  const vanOf = new Map<string, DecadeFacts>((chart.decades as DecadeFacts[]).map(d => [d.palace, d]));
  const decades: DecadeRaw[] = (chart.decades as DecadeFacts[]).slice(0, 10).map(d => {
    const hv = hoaItems(c, d.hoa, d.palace, 'hoa_van', d.stem);
    const vv = [...vanItems(d.palace, 'van', d.readings, toanThuLines(chart, d, 99), d.kl), ...dauItems(chart, c.byName.get(d.palace)!, 'van', 'vận'), ...dhItems(c, d.palace, 'van', d.kl, 'vận')];
    const n = countOf(vv);
    return { d, layers: [
      { layer: 'hoa_van', raw: net(hv), items: hv, basis: 'thong_le', note: `Tứ Hóa theo can ${d.stem}: ${hv.length} hóa trong tam phương cung vận hoặc Mệnh` },
      { layer: 'van', raw: net(vv), items: vv, basis: 'sach', note: `cung vận ${d.palace}: ${n.s} câu sách, ${n.d} sao xét đắc hãm (KL tr.233)` },
    ] };
  });

  // the years: tiểu hạn by the chart's school, lưu đại hạn inside the đại hạn, lưu stars of the year
  const Y0 = chart.year.year, born = chart.lunar_year;
  const factsRule = tieuHanRule(chart), rule = opts.tieuHanRule ?? factsRule;
  const dhDir: 1 | -1 = /nghịch/.test(chart.dai_han_direction) ? -1 : 1;
  // the Tứ Hóa of each stem, as the Python engine placed it for the đại hạn stems (one table, no copy of it here)
  const hoaOfStem = new Map<string, ChartInput['decades'][number]['hoa']>(chart.decades.map(d => [d.stem, d.hoa]));
  const yf = chart.year as ChartInput['year'] & { tieu_han_tt?: DecadeFacts['tt']; tieu_han_kl?: DecadeFacts['kl']; nguyet_han?: Record<string, number> | null };
  const years: YearRaw[] = [];
  if (BRANCHES.includes(chart.year_gz?.split(' ')[1] ?? '')) for (let y = Y0 - span; y <= Y0 + span; y++) {
    const age = y - born + 1;
    if (age < 1) continue;
    const p = c.byIndex.get(tieuHanBranch(chart, age, rule))!;
    const stem = STEMS[(((y - 4) % 10) + 10) % 10], ybr = BRANCHES[(((y - 4) % 12) + 12) % 12];
    const tt = c.byBranch.get(ybr)!;
    const di = chart.decades.slice(0, 10).findIndex(d => d.age_from <= age && age <= d.age_to), d = di >= 0 ? chart.decades[di] : null;
    const vd = vanOf.get(p.name);
    // the viewed year carries its own Toàn Thư / Khảo Luận facts for the tiểu hạn palace (facts.year); they equal the decade entry of that palace
    const own = y === Y0 && rule === factsRule && yf.tieu_han_palace === p.name;
    const th = [...vanItems(p.name, 'tieu_han', vd?.readings ?? [], vd ? toanThuLines(chart, vd, 99) : [], own && yf.tieu_han_kl ? yf.tieu_han_kl : vd?.kl,
      '', d?.palace === p.name ? 'trung_phung' : 'tieu'),
      ...dauItems(chart, p, 'tieu_han', 'tiểu hạn'), ...dhItems(c, p.name, 'tieu_han', null, 'tiểu hạn')];
    const ld = d ? c.byIndex.get(luuDaiHanBranch(c.byName.get(d.palace)!.branch_index, dhDir, age - d.age_from))! : null, ldv = ld ? vanOf.get(ld.name) : undefined;
    const lh = ld ? [...vanItems(ld.name, 'luu_dai_han', ldv?.readings ?? [], ldv ? toanThuLines(chart, ldv, 99) : [], ldv?.kl, LDH_CITE), ...dauItems(chart, ld, 'luu_dai_han', 'lưu đại hạn', LDH_CITE),
      ...dhItems(c, ld.name, 'luu_dai_han', ldv?.kl ?? null, 'lưu đại hạn', LDH_CITE)] : [];
    // TH p.115 IX.3-4: the Bắc đẩu stars of the đại hạn palace weigh in its first five years, its Nam đẩu stars in the last five
    const half = d && age - d.age_from < 5 ? 'bac' : 'nam';
    const dt = d ? decades[di].layers.find(l => l.layer === 'van')!.items
      .filter(i => i.id.startsWith('KL233_') && i.scope === 'self' && (dauOf(i.star!) === half || dauOf(i.star!) === 'ca_hai'))
      .map(i => ({ ...i, layer: 'dau_tinh' as Layer, cite: `${i.cite}; TH tr.115 mục IX.${half === 'bac' ? 3 : 4} (${DAU_VI[half]} ứng mạnh ở năm năm ${half === 'bac' ? 'đầu' : 'sau'} của đại hạn), sao ${DAU_VI[half]}: TH tr.${DAU_TINH[i.star!].page}` })) : [];
    const luu = luuStars(chart, y);
    const all = luuItems(c, p.name, luu);
    // the lưu stars split by basis: TH tr.114 (Khốc, Hư at the tiểu hạn) is book; the side of Kình, Đà, Lộc Tồn and of Khốc, Hư elsewhere is convention
    const ls = all.filter(i => i.basis === 'sach'), lt = all.filter(i => i.basis !== 'sach').map(i => ({ ...i, layer: 'luu_sao_tl' as Layer }));
    // lưu Tứ Hóa: the same four stars as the decade's when the year stem is the decade stem — counted once, in the decade
    const sameStem = !!d && d.stem === stem, lh4 = sameStem ? [] : hoaItems(c, hoaOfStem.get(stem), p.name, 'luu_tu_hoa', stem);
    const nt = countOf(th), nl = countOf(lh);
    years.push({ year: y, age, can_chi: `${stem} ${ybr}`, palace: p.name, branch: p.branch, thai_tue: tt.name, luu_dai_han: ld?.name ?? null, decade: di >= 0 ? di : null, luu, layers: [
      { layer: 'tieu_han', raw: net(th), items: th, basis: 'sach', note: `cung tiểu hạn ${p.name} (${rule === 'KL' ? 'Khảo Luận tr.39-40, theo âm dương' : 'Thực Hành tr.27, nam thuận nữ nghịch'}): ${nt.s} câu sách, ${nt.d} sao xét đắc hãm` },
      { layer: 'luu_dai_han', raw: net(lh), items: lh, basis: 'sach', note: ld ? `cung lưu đại hạn ${ld.name} (TH tr.117-118): ${nl.s} câu sách, ${nl.d} sao xét đắc hãm` : 'chưa vào đại hạn đầu tiên: không có lưu đại hạn' },
      { layer: 'dau_tinh', raw: net(dt), items: dt, basis: 'sach', note: d ? `TH tr.115: năm thứ ${age - d.age_from + 1} của đại hạn, sao ${DAU_VI[half]} của cung ${d.palace} ứng mạnh: ${dt.length}` : 'chưa vào đại hạn đầu tiên' },
      { layer: 'luu_sao', raw: net(ls), items: ls, basis: 'sach', note: `Thực Hành tr.114: lưu Khốc, Hư ở cung tiểu hạn năm ${stem} ${ybr}: ${ls.length}` },
      { layer: 'luu_sao_tl', raw: net(lt), items: lt, basis: 'thong_le', note: `sao lưu năm ${stem} ${ybr} theo loại sao, trong tầm tiểu hạn hoặc Mệnh: ${lt.length}` },
      { layer: 'luu_tu_hoa', raw: net(lh4), items: lh4, basis: 'thong_le', note: sameStem ? `can năm ${stem} trùng can đại vận: lưu Tứ Hóa đã tính trong chặng, không cộng lần nữa` : `lưu Tứ Hóa theo can ${stem} trong tầm tiểu hạn hoặc Mệnh: ${lh4.length}` },
    ] });
  }
  // the months of the viewed year: tháng Giêng counted from the tiểu hạn palace back to the birth month, then Tý forward to the birth hour
  // (TH p.115, KL pp.40-41). The engine counted it from its own tiểu hạn; the step from the tiểu hạn to tháng Giêng depends only on the
  // birth month and hour, so the same step is taken from the tiểu hạn of this school.
  let months: MonthRaw[] | null = null;
  const b0 = BRANCHES.indexOf(yf.tieu_han_branch ?? ''), first = yf.nguyet_han ? Object.entries(yf.nguyet_han).find(([, mo]) => mo === 1)?.[0] : undefined;
  if (b0 >= 0 && first && c.byName.has(first)) {
    const m1 = tieuHanBranch(chart, Y0 - born + 1, rule) + c.byName.get(first)!.branch_index - b0;
    months = Array.from({ length: 12 }, (_, i) => {
      const p = c.byIndex.get(mod12(m1 + i))!, it = dhItems(c, p.name, 'nguyet', null, 'nguyệt hạn');
      return { month: i + 1, palace: p.name, layer: { layer: 'nguyet' as Layer, raw: net(it), items: it, basis: 'sach' as const, note: `cung nguyệt hạn ${p.name} và tam phương: ${it.length} sao xét đắc hãm (KL tr.233)` } };
    });
  }
  return { Y0, rule, palaces, natalNet, than: chart.palaces.find(p => p.is_than && p.name !== 'Mệnh')?.name ?? null, decades, years, months };
}

// ================================================================ scoring ================================================================

/** One layer of a period score: raw net, its scaled value against the corpus, its weight and what it adds (value = weight × z). */
export interface Part { layer: Layer; raw: number; z: number; weight: number; value: number; note: string; basis: ItemBasis | 'tinh_toan' }
/** A labelled line of the "Căn cứ" fold that is not a scored item (TH p.118 cách, the insufficient flag). */
export interface Note { text: string; cite: string; basis: ItemBasis | 'tinh_toan' }
export interface Period { score: number; level: number; level_vi: string; insufficient: boolean; parts: Part[]; items: Item[]; notes: Note[]; text: string[] }
export interface DecadeIndex extends Period { index: number; palace: string; branch: string; stem: string; age_from: number; age_to: number; year_from: number; year_to: number; current: boolean }
export interface YearIndex extends Period { year: number; age: number; can_chi: string; palace: string; branch: string; thai_tue: string; luu_dai_han: string | null; current: boolean; decade: number | null }
/** A month with nothing of its own to read has no level (null, "Chưa xác định"); its score is then the year's. */
export interface MonthIndex extends Omit<Period, 'level'> { level: number | null; month: number; palace: string }
export interface BaziStrip {
  basis: string; cell: string | null; note: string;
  pillars: Array<{ index: number; pillar: string; age_from: number; year_from: number | null; year_to: number | null; tag: 'dung' | 'hy' | 'khong';
    tag_vi: string; reduced: string | null; current: boolean }>;
}
export interface Indices {
  version: string; disclaimer: string; year: number; levels: readonly string[];
  /** the tiểu hạn school the years and months follow, in words */
  tieu_han_rule: { rule: 'KL' | 'TH'; label: string };
  palaces: PalaceIndex[]; decades: DecadeIndex[]; years: YearIndex[];
  months: { year: number; basis: string; months: MonthIndex[]; note?: string } | null;
  bazi: BaziStrip | null;
  /** the level cut points the charts draw as bands (norms.cuts) */
  cuts: { decade: number[]; year: number[]; month: number[] } | null;
  norms: { version: string; kbVersion: string; charts: number; corpus: string } | null;
  method: Record<string, string>;
  /** what the radar's Tật Ách point is and is not (owner's decision 2026-10-24) */
  radar_note: string;
}
export const UNDETERMINED_VI = 'Chưa xác định';
export const TAT_ACH_NOTE = 'Cung Tật Ách trên biểu đồ là đánh giá cát hung theo Tử Vi, không phải dự đoán sức khỏe hay chẩn đoán y khoa.';
const RULE_VI = { KL: 'Khảo Luận tr.39-40: dương nam, âm nữ đi thuận; âm nam, dương nữ đi nghịch (mặc định)', TH: 'Thực Hành tr.27: nam đi thuận, nữ đi nghịch' } as const;

/** A layer's raw value in its typical corpus size (root mean square): not centred, so a layer with nothing adds 0. */
export const zOf = (norms: IndexNorms | null, key: string, raw: number) => {
  const n = norms?.layers?.[key], u = n ? n.rms || n.sd : 0;
  return u ? r3(raw / u) : r3(raw);
};
/** Level 0 … 4 (index into LEVELS): how many cut points the score reaches. */
export function levelOf(score: number, cuts: number[] | undefined): number {
  return (cuts ?? FALLBACK_CUTS).filter(x => score >= x).length;
}
const part = (norms: IndexNorms | null, l: RawLayer, weight: number, key: string = l.layer): Part => {
  const z = zOf(norms, key, l.raw);
  return { layer: l.layer, raw: l.raw, z, weight, value: r3(weight * z), note: l.note, basis: l.basis };
};
/** Book evidence of a period: at least one book item in a non-convention layer. */
export const hasBook = (layers: RawLayer[]) => layers.some(l => !CONVENTION.has(l.layer) && l.items.some(SOURCED));

/** The convention cap: the convention parts may add at most CONV_K × |sourced| (+ CONV_FLOOR when they agree with the books or the books
 *  are silent); against the books at most CONV_K × |sourced|, so the books' direction stands. Returns the correction part, or null. */
export function conventionCap(parts: Part[]): Part | null {
  const S = parts.filter(p => !CONVENTION.has(p.layer)).reduce((a, p) => a + p.value, 0);
  const C = parts.filter(p => CONVENTION.has(p.layer)).reduce((a, p) => a + p.value, 0);
  const agree = S === 0 || Math.sign(C) === Math.sign(S);
  const bound = CONV_K * Math.abs(S) + (agree ? CONV_FLOOR : 0);
  const capped = Math.max(-bound, Math.min(bound, C));
  if (Math.abs(capped - C) < 0.0005) return null;
  return { layer: 'thong_le_cap', raw: r3(C), z: r3(capped), weight: 1, value: r3(capped - C), basis: 'tinh_toan',
    note: `phần thông lệ ${vn(C)} giới hạn còn ${vn(capped)}: thông lệ chỉ ${agree ? 'nhấn thêm' : 'làm dịu'} chiều của sách (${vn(S)}), không lật được` };
}
/** Decade score: Σ weight × z with the convention cap. */
export function scoreDecade(norms: IndexNorms | null, layers: RawLayer[]): { score: number; parts: Part[] } {
  const parts = layers.map(l => part(norms, l, W_DECADE[l.layer as keyof typeof W_DECADE] ?? 0));
  const cap = conventionCap(parts);
  if (cap) parts.push(cap);
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}
export function scoreYear(norms: IndexNorms | null, layers: RawLayer[], decadeScore: number | null): { score: number; parts: Part[] } {
  const parts: Part[] = [];
  if (decadeScore !== null) {
    const z = zOf(norms, 'dai_van', decadeScore);
    parts.push({ layer: 'dai_van', raw: decadeScore, z, weight: W_YEAR.dai_van, value: r3(W_YEAR.dai_van * z), basis: 'tinh_toan', note: 'mức của đại vận đang đi' });
  }
  for (const l of layers) parts.push(part(norms, l, W_YEAR[l.layer as keyof typeof W_YEAR] ?? 0));
  const cap = conventionCap(parts);
  if (cap) parts.push(cap);
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}
export function scoreMonth(norms: IndexNorms | null, l: RawLayer, yearScore: number): { score: number; parts: Part[] } {
  const parts: Part[] = [{ layer: 'nam', raw: yearScore, z: yearScore, weight: 1, value: yearScore, basis: 'tinh_toan', note: 'mức của năm' }, part(norms, l, W_MONTH)];
  return { score: r3(parts.reduce((a, p) => a + p.value, 0)), parts };
}

export interface ScoredPeriod { score: number; book: boolean }
/** Scores of every period of one chart, without words (tools/interpret/index_norms.ts places the cut points on the ones with book evidence). */
export function periodScores(inp: PeriodInputs, norms: IndexNorms | null): { decades: ScoredPeriod[]; years: ScoredPeriod[]; months: ScoredPeriod[] } {
  const decades = inp.decades.map(d => ({ score: scoreDecade(norms, d.layers).score, book: hasBook(d.layers) }));
  const years = inp.years.map(y => {
    const dec = y.decade === null ? null : decades[y.decade];
    return { score: scoreYear(norms, y.layers, dec ? dec.score : null).score, book: hasBook(y.layers) || !!dec?.book };
  });
  const i0 = inp.years.findIndex(y => y.year === inp.Y0);
  const ys = i0 >= 0 ? years[i0].score : null;
  return { decades, years, months: ys === null || !inp.months ? [] : inp.months.map(m => ({ score: scoreMonth(norms, m.layer, ys).score, book: m.layer.items.length > 0 })) };
}

// ================================================================ words ================================================================

const cap = (s: string) => s ? s[0].toUpperCase() + s.slice(1) : s;
const joinVi = (xs: string[]) => xs.length < 2 ? (xs[0] ?? '') : `${xs.slice(0, -1).join(', ')} và ${xs.at(-1)}`;
const bookTag = (it: Item) => it.book ? ` (${it.book}${it.basis === 'sach_dien_giai' ? ', diễn ý' : ''})` : '';
const topBy = (xs: Item[], side: Side, n: number) => {
  const seen = new Set<string>();
  return xs.filter(x => x.side === side && x.gist).sort((a, b) => b.w - a.w || (a.id < b.id ? -1 : 1)).filter(x => !seen.has(x.gist!) && !!seen.add(x.gist!)).slice(0, n);
};
/** "đắc địa có Thái Âm, Thiên Cơ; hãm địa có Tham Lang" (the strongest three a side), or '' when no star was read. */
function dacClause(items: Item[]): string {
  const dh = items.filter(i => i.id.startsWith('KL233_'));
  const names = (side: Side) => [...new Set(dh.filter(i => i.side === side).map(i => i.id === 'KL233_HAM_GIAI' ? `${i.star} (hãm, có Tuần Triệt giải)` : i.star!))].slice(0, 3);
  const g = names('support'), b = names('limit');
  return [g.length ? `đắc địa có ${joinVi(g)}` : '', b.length ? `hãm địa có ${joinVi(b)}` : ''].filter(Boolean).join('; ');
}
/** "Sách về vận ghi: A (Khảo Luận); ngược lại, B (Thực Hành); xét đắc hãm các sao, đắc địa có …" — or '' when nothing was read. */
function bookSentence(items: Item[], lead: string, dacLead: string): string {
  const pos = topBy(items, 'support', 2), neg = topBy(items, 'limit', pos.length ? 1 : 2);
  const say = (xs: Item[]) => xs.map(x => `${x.gist}${bookTag(x)}`).join('; ');
  const said = `${pos.length ? say(pos) : ''}${pos.length && neg.length ? '; ngược lại, ' : ''}${neg.length ? say(neg) : ''}`, dac = dacClause(items);
  if (!said && !dac) return '';
  if (!said) return `${cap(dacLead)} ${dac}.`;
  return `${lead} ${said}${dac ? `; ${dacLead} ${dac}` : ''}.`;
}
/** "Hóa Quyền và Hóa Khoa vào ngay cung vận, Hóa Lộc vào Thiên Di (tam hợp)": names grouped by where they land, in first-seen order. */
function byPlace(xs: Item[], name: (i: Item) => string, home: string, verb: string): string {
  const g = new Map<string, string[]>();
  for (const i of xs) { const w = where(i, home); g.set(w, [...(g.get(w) ?? []), name(i)]); }
  return joinVi([...g.entries()].map(([w, ns]) => `${joinVi(ns)} ${verb} ${w}`));
}
const where = (it: Item, home: string) => it.scope === 'self' ? home : it.scope === 'menh' ? 'Mệnh' : `${it.palace} (${REL_VI[it.scope]})`;

function hoaSentence(items: Item[], stem: string, home: string, scopeWord: string): string {
  const good = items.filter(i => i.side === 'support').sort((a, b) => b.w - a.w), bad = items.filter(i => i.side === 'limit');
  const name = (i: Item) => i.text.split(' của ')[0];
  const goods = byPlace(good, name, home, 'vào'), bads = byPlace(bad, name, home, 'vào');
  if (!good.length && !bad.length) return `Tứ Hóa theo can ${stem} đều rơi ngoài tam phương ${scopeWord} và Mệnh, nên ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này ít chịu tác động của Tứ Hóa.`;
  if (good.length && bad.length) return `Theo thông lệ, can ${stem} đưa ${goods}, thêm lực cho ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này; nhưng ${bads}, kéo theo trở ngại ở đó.`;
  if (good.length) return `Theo thông lệ, can ${stem} đưa ${goods}, thêm lực cho ${scopeWord === 'cung vận' ? 'chặng' : 'năm'} này, còn Hóa Kỵ ở ngoài tầm.`;
  return `Theo thông lệ, can ${stem} đưa ${bads}, trong khi Lộc, Quyền, Khoa đều ngoài tầm, nên đây là điểm cần dè chừng.`;
}
/** The book side of a period: support − limit of its book items (convention left out). */
const bookNet = (items: Item[]) => r3(items.filter(SOURCED).reduce((a, i) => a + (i.side === 'support' ? i.w : -i.w), 0));
const bothSides = (items: Item[]) => items.some(i => SOURCED(i) && i.side === 'support') && items.some(i => SOURCED(i) && i.side === 'limit');
const softened = (parts: Part[]) => parts.some(p => p.layer === 'thong_le_cap' && Math.sign(p.value) === Math.sign(parts.filter(q => !CONVENTION.has(q.layer) && q.layer !== 'thong_le_cap').reduce((x, q) => x + q.value, 0)));
const thinSentence = (what: string, where: string) =>
  `Tính chung, ${what} chưa có lời sách nào về ${where} (chỉ có thông lệ), nên tạm để mức “${LEVELS[LEVEL_DEFAULT]}”: ${INSUFFICIENT_VI}, không có nghĩa là ${what} thật sự trung bình.`;
const thinNote = (what: string): Note => ({ text: `${cap(what)} không có câu sách hay sao nào đã đối chiếu độ sáng để xét: mức “${LEVELS[LEVEL_DEFAULT]}” chỉ là mặc định, ${INSUFFICIENT_VI}.`,
  cite: 'quy ước hệ thống (chủ dự án quyết định 2026-10-24)', basis: 'tinh_toan' });

/** TH p.118 "Các cách dùng cho đại tiểu hạn" 1-2: Mệnh / Thân sáng sủa or hắc ám against a good hạn. Words and a note, never a score. */
type MenhState = { state: 'sang' | 'toi' | null; zm: number; zt: number | null };
function menhState(inp: PeriodInputs, norms: IndexNorms | null): MenhState {
  const zm = zOf(norms, 'vung', inp.natalNet['Mệnh'] ?? 0), zt = inp.than ? zOf(norms, 'vung', inp.natalNet[inp.than] ?? 0) : null;
  const t = zt ?? zm;
  return { state: zm >= MENH_Z && t >= 0 ? 'sang' : zm <= -MENH_Z && t <= 0 ? 'toi' : null, zm, zt };
}
function th118(ms: MenhState, level: number, than: string | null): { tail: string; note: Note | null } {
  const who = than ? `Mệnh và Thân (cung ${than})` : 'Mệnh';
  const z = `${who}: ${vn(ms.zm)}${ms.zt !== null ? ` / ${vn(ms.zt)}` : ''} lần cỡ thường gặp so với lá số mẫu; ngưỡng ±${vn(MENH_Z)} là thông lệ hệ thống`;
  const mk = (tail: string, cach: string, item: number) => ({ tail, note: { text: `${cach} (${z}).`, cite: `TH tr.118 “Các cách dùng cho đại tiểu hạn” mục ${item}`, basis: 'sach' as const } });
  if (ms.state === 'sang' && level === 4) return mk('; Mệnh sáng sủa lại gặp hạn rực rỡ, Thực Hành gọi là cách “thêm gấm thêm hoa”', 'Mệnh sáng sủa gặp hạn rực rỡ: “thêm gấm thêm hoa”', 1);
  if (ms.state === 'toi' && level === 4) return mk('; Mệnh vốn kém sáng mà gặp hạn rực rỡ, Thực Hành gọi là “rồng mây gặp hội”: gốc kém không làm giảm cái tốt của hạn', 'Mệnh hắc ám gặp hạn rực rỡ: “rồng mây gặp hội”', 2);
  if (ms.state === 'toi' && level === 3) return mk('; Mệnh vốn kém sáng gặp hạn tốt vừa, Thực Hành gọi là “cây khô gặp mùa xuân”', 'Mệnh hắc ám gặp hạn tốt vừa: “cây khô gặp mùa xuân”', 2);
  if (ms.state === 'toi' && level <= 1) return { tail: '; Mệnh vốn kém sáng mà hạn cũng khó: Thực Hành không nói thêm cho trường hợp này, nên mức chỉ theo lời sách về cung vận',
    note: { text: `Mệnh kém sáng gặp hạn khó: Thực Hành tr.118 chỉ nêu cách cho hạn tốt, nên không cộng hay trừ gì thêm (${z}).`, cite: 'TH tr.118 mục 1-2 (không nói trường hợp này)', basis: 'tinh_toan' } };
  return { tail: '', note: null };
}

function decadeText(d: DecadeFacts, y1: number, y2: number, parts: Part[], layers: RawLayer[], level: number, insufficient: boolean, t118: string): string[] {
  const out: string[] = [];
  const ev = d.kl?.event, dom = DOMAIN[d.palace];
  out.push(`Chặng ${d.age_from}–${d.age_to} tuổi mụ (${y1}–${y2}) đi qua cung ${d.palace}${ev ? `, nên theo Khảo Luận biến cố của chặng thường liên quan đến ${ev}` : dom ? ` (cung của ${dom})` : ''}.`);
  out.push(hoaSentence(layers.find(l => l.layer === 'hoa_van')!.items, d.stem, 'ngay cung vận', 'cung vận'));
  const van = layers.find(l => l.layer === 'van')!.items;
  const b = bookSentence(van, 'Sách về vận ghi:', 'xét đắc hãm các sao (Khảo Luận),');
  if (b) out.push(b);
  if (insufficient) { out.push(thinSentence('chặng này', `cung ${d.palace}`)); return out.map(cap); }
  const S = bookNet(van);
  // the level compares with the typical decade; when it goes the other way of the books' own side, say so (owner's plan 2026-10-24: explain, never force)
  const weigh = van.some(i => TRIAD_RULES.has(i.id)) && level <= 1 ? '; Khảo Luận coi vị trí tam hợp Thái Tuế là may mắn nhất, nhưng các lời sách khác về chặng này kém hơn những chặng thường gặp'
    : S > 0 && level <= 1 ? '; lời sách về chặng này vẫn nghiêng về thuận, nhưng ít điều thuận hơn những chặng thường gặp'
    : S < 0 && level >= 3 ? '; lời sách về chặng này nghiêng về bất lợi, nhưng nhẹ hơn những chặng thường gặp'
    : bothSides(van) ? `; lời sách có cả hai chiều, bên ${S >= 0 ? 'thuận' : 'bất lợi'} nặng hơn` : '';
  out.push(`Tính chung, chặng này ở mức “${LEVELS[level]}” so với các chặng thường gặp${weigh}${t118}${softened(parts) ? '; phần theo thông lệ chỉ làm dịu bớt, không đổi chiều của lời sách' : ''}.`);
  return out.map(cap);
}

const WHY: Partial<Record<Layer, string>> = { dai_van: 'phần lớn theo đà của đại vận đang đi', tieu_han: 'phần lớn do cung tiểu hạn', luu_dai_han: 'phần lớn do cung lưu đại hạn',
  dau_tinh: 'phần lớn do các sao Nam, Bắc đẩu của cung đại vận', luu_sao: 'phần lớn do sao lưu ở cung tiểu hạn' };
function yearText(y: YearRaw, dec: DecadeIndex | null, level: number, parts: Part[], insufficient: boolean): string[] {
  const out: string[] = [];
  const dom = DOMAIN[y.palace], L = (l: Layer) => y.layers.find(x => x.layer === l)!.items;
  out.push(`Năm ${y.year} (${y.can_chi}), ${y.age} tuổi mụ, ${dec ? `nằm trong chặng ${dec.age_from}–${dec.age_to} (cung ${dec.palace}, mức “${dec.level_vi}”${dec.insufficient ? `, ${INSUFFICIENT_VI}` : ''})` : 'chưa vào đại vận đầu tiên'}; tiểu hạn ở cung ${y.palace}${dom ? ` (cung của ${dom})` : ''}${y.luu_dai_han ? `, lưu đại hạn ở cung ${y.luu_dai_han}` : ''}.`);
  const th = L('tieu_han'), ld = L('luu_dai_han');
  // tiểu hạn in the đại vận's own palace: the decade panel already quotes the same sentences
  let b = dec && dec.palace === y.palace ? (th.length ? `Tiểu hạn trùng cung đại vận, nên những lời sách về cung ${y.palace} của chặng này được nhấn thêm trong năm` : '')
    : bookSentence(th, 'Sách về vận ghi cho cung tiểu hạn:', 'xét đắc hãm các sao của cung tiểu hạn,').replace(/\.$/, '');
  if (ld.some(SOURCED) && y.luu_dai_han !== y.palace) {
    const n = bookNet(ld), lead = topBy(ld, n >= 0 ? 'support' : 'limit', 1)[0];
    const c = `cung lưu đại hạn ${y.luu_dai_han} nghiêng về ${n >= 0 ? 'thuận' : 'bất lợi'} theo sách${lead ? ` (${lead.gist})` : ''}`;
    b = b ? `${b}; ${c}` : cap(c);
  }
  if (b) out.push(`${b}.`);
  const ls = [...L('luu_sao'), ...L('luu_sao_tl')], lh = L('luu_tu_hoa'), dt = L('dau_tinh');
  const bits: string[] = [];
  if (dt.length) {
    const g = /IX\.3/.test(dt[0].cite) ? 'bac' : 'nam';
    bits.push(`theo Thực Hành, năm này ở ${g === 'bac' ? 'năm năm đầu' : 'năm năm sau'} của đại hạn, lúc ${DAU_VI[g]} tinh của cung đại vận (${joinVi([...new Set(dt.map(i => i.star!))])}) ứng mạnh`);
  }
  const kh = ls.filter(i => (i.id === 'LUU_KHOC' || i.id === 'LUU_HU') && i.scope === 'self');
  const khNames = joinVi(kh.map(i => i.text.slice(4).split(' ở ')[0]));
  if (ls.some(i => i.id === 'TH_LUU_KHOC_HU_HUNG')) bits.push(`lưu ${khNames} gặp hung tinh ngay cung tiểu hạn, Thực Hành gọi là năm đầy tai ương, nước mắt`);
  else if (kh.length) bits.push(`lưu ${khNames} đến ngay cung tiểu hạn, Thực Hành coi là điềm xấu`);
  const others = ls.filter(i => !kh.includes(i) && i.id !== 'TH_LUU_KHOC_HU_HUNG');
  for (const side of ['limit', 'support'] as Side[]) {
    const xs = others.filter(i => i.side === side);
    if (xs.length) bits.push(`lưu ${byPlace(xs, i => i.text.slice(4).split(' ở ')[0], 'cung tiểu hạn', 'ở')}${side === 'limit' ? ' thêm sức cản' : ' thêm chút thuận'}`);
  }
  if (lh.length) bits.push(`theo thông lệ lưu Tứ Hóa, ${byPlace(lh, i => i.text.split(' của ')[0], 'cung tiểu hạn', 'vào')}`);
  if (bits.length) out.push(`${cap(bits.slice(0, 3).join('; '))}.`);
  if (insufficient) { out.push(thinSentence('năm này', 'cung tiểu hạn, cung lưu đại hạn hay chặng đang đi')); return out.map(cap); }
  const lead = [...parts].filter(p => WHY[p.layer]).sort((a, b) => Math.abs(b.value) - Math.abs(a.value))[0];
  const why = lead && Math.abs(lead.value) >= 0.2 ? WHY[lead.layer]! : '';
  // a year may go the other way of its decade when its own palaces say so; the words then say why
  const other = dec && !dec.insufficient && (dec.level - 2) * (level - 2) < 0;
  out.push(`Tính chung năm ${y.year} ở mức “${LEVELS[level]}”${other ? `, khác chiều với chặng đang đi${why && lead.layer !== 'dai_van' ? `, ${why}` : ''}` : why ? `, ${why}` : ''}${softened(parts) ? '; phần theo thông lệ chỉ làm dịu bớt, không đổi chiều của lời sách' : ''}.`);
  return out.map(cap);
}

function monthText(m: MonthRaw, Y0: number, year: YearIndex, level: number | null, z: number): string[] {
  const head = `Tháng ${m.month} âm lịch rơi vào cung ${m.palace}${DOMAIN[m.palace] ? ` (cung của ${DOMAIN[m.palace]})` : ''}, theo cách an nguyệt hạn từ cung tiểu hạn.`;
  if (level === null) return [head, `Cung tháng và tam phương không có sao nào đã đối chiếu độ sáng để xét đắc hãm, nên chưa xác định được mức riêng của tháng; mức chung của năm ${Y0} là “${year.level_vi}”.`];
  return [head, `Xét đắc hãm các sao của cung tháng và tam phương (Khảo Luận): ${dacClause(m.layer.items)}.`,
    `Mức của tháng là mức của năm ${Y0}${Math.abs(z) >= 0.5 ? `, ${z > 0 ? 'nhích lên' : 'nhích xuống'} theo cung này` : ', gần như không đổi theo cung này'}: “${LEVELS[level]}”.`];
}

// ================================================================ Bát Tự strip ================================================================

const DH_TAG = { dung: 'Mang thần điều hậu (dụng)', hy: 'Mang thần điều hậu (hỷ)', khong: 'Không mang thần điều hậu' } as const;
function baziStrip(chart: ChartInput, Y0: number): BaziStrip | null {
  const b = chart.bazi, D = b?.deep;
  if (!b || !D?.luck?.length || !D.dieu_hau?.verified) return null;
  const luck = b.luck;
  const pillars = D.luck.map((l, i) => {
    const L = luck.find(x => x.name === l.pillar) ?? luck[l.index - 1];
    const roles = [l.dieu_hau?.stem, l.dieu_hau?.branch];
    const tag = roles.includes('yong') ? 'dung' : roles.includes('xi') ? 'hy' : 'khong';
    const next = D.luck[i + 1] && (luck.find(x => x.name === D.luck[i + 1].pillar) ?? luck[D.luck[i + 1].index - 1]);
    const yf = L?.start_year ?? null, yt = next?.start_year != null ? next.start_year - 1 : yf !== null ? yf + 9 : null;
    const red = l.findings.find(f => /DIEU_HAU/.test(f.rule_id));
    return { index: l.index, pillar: l.pillar, age_from: Math.round(L?.start_age ?? 0), year_from: yf, year_to: yt, tag: tag as 'dung' | 'hy' | 'khong', tag_vi: DH_TAG[tag],
      reduced: red ? red.text : null, current: yf !== null && yt !== null && yf <= Y0 && Y0 <= yt };
  });
  return { basis: 'Thiệu Vĩ Hoa tr.389-396 (bảng điều hậu)', cell: D.dieu_hau.cell, pillars,
    note: 'Bảng điều hậu chỉ ghi thần cần dùng; vận không mang thần ấy được để trống, không gọi là kỵ. Dải này đặt cạnh để đối chiếu, không cộng vào mức Tử Vi.' };
}


// ================================================================ all indices ================================================================

/** All indices for one chart; `year` is the facts' viewed year (facts.year.year). Deterministic: same facts, knowledge and norms → same output. */
export function computeIndices(chart: ChartInput, k: Knowledge, norms: IndexNorms | null, span = 10, opts: { tieuHanRule?: 'KL' | 'TH' } = {}): Indices {
  const inp = periodInputs(chart, k, norms, span, opts);
  const Y0 = chart.year.year, born = chart.lunar_year, cur = chart.year.dai_han;
  const ms = menhState(inp, norms);
  const decades: DecadeIndex[] = inp.decades.map(({ d, layers }) => {
    const { score, parts } = scoreDecade(norms, layers);
    const insufficient = !hasBook(layers);
    const level = insufficient ? LEVEL_DEFAULT : levelOf(score, norms?.cuts?.decade);
    const y1 = born + d.age_from - 1, y2 = born + d.age_to - 1;
    const t = insufficient ? { tail: '', note: null } : th118(ms, level, inp.than);
    return { index: d.index, palace: d.palace, branch: d.branch, stem: d.stem, age_from: d.age_from, age_to: d.age_to, year_from: y1, year_to: y2,
      current: !!cur && cur.age_from === d.age_from, score, level, level_vi: LEVELS[level], insufficient, parts,
      items: layers.flatMap(l => l.items), notes: [...(t.note ? [t.note] : []), ...(insufficient ? [thinNote('chặng này')] : [])],
      text: decadeText(d, y1, y2, parts, layers, level, insufficient, t.tail) };
  });
  const years: YearIndex[] = inp.years.map(y => {
    const dec = y.decade === null ? null : decades[y.decade];
    const { score, parts } = scoreYear(norms, y.layers, dec ? dec.score : null);
    const insufficient = !hasBook(y.layers) && (!dec || dec.insufficient);
    const level = insufficient ? LEVEL_DEFAULT : levelOf(score, norms?.cuts?.year);
    return { year: y.year, age: y.age, can_chi: y.can_chi, palace: y.palace, branch: y.branch, thai_tue: y.thai_tue, luu_dai_han: y.luu_dai_han, current: y.year === Y0, decade: y.decade,
      score, level, level_vi: LEVELS[level], insufficient, parts, items: y.layers.flatMap(l => l.items), notes: insufficient ? [thinNote('năm này')] : [],
      text: yearText(y, dec, level, parts, insufficient) };
  });
  const yv = years.find(y => y.current);
  const months = inp.months && yv ? { year: Y0, basis: 'vị trí: TH tr.115, KL tr.40-41 (từ cung tiểu hạn); mức của tháng = mức của năm, nhích theo đắc hãm các sao của cung nguyệt hạn và tam phương (KL tr.233 mục 4)',
    months: inp.months.map(m => {
      const { score, parts } = scoreMonth(norms, m.layer, yv.score);
      const level = m.layer.items.length ? levelOf(score, norms?.cuts?.month) : null;
      return { month: m.month, palace: m.palace, score, level, level_vi: level === null ? UNDETERMINED_VI : LEVELS[level], insufficient: level === null, parts, items: m.layer.items,
        notes: level === null ? [{ text: 'Cung tháng và tam phương không có sao nào đã đối chiếu độ sáng: tháng không có mức riêng.', cite: 'quy ước hệ thống (chủ dự án quyết định 2026-10-24)', basis: 'tinh_toan' as const }] : [],
        text: monthText(m, Y0, yv, level, parts[1].z) };
    }) } : null;
  // twelve months on one level: the chart is flat on purpose (no invented variation, owner 2026-10-24); the card says why
  if (months) { const lv = [...new Set(months.months.filter(x => x.level !== null).map(x => x.level_vi))];
    if (lv.length === 1 && months.months.filter(x => x.level !== null).length >= 6) (months as typeof months & { note?: string }).note =
      `Các tháng cùng ở mức “${lv[0]}”: đắc hãm các sao ở cung nguyệt hạn từng tháng chỉ nhích quanh mức của năm, chưa tháng nào đủ đổi bậc.`; }

  return {
    version: INDICES_VERSION, disclaimer: DISCLAIMER, year: Y0, levels: LEVELS, tieu_han_rule: { rule: inp.rule, label: RULE_VI[inp.rule] },
    palaces: inp.palaces, decades, years, months, bazi: baziStrip(chart, Y0), cuts: norms?.cuts ?? null,
    norms: norms && { version: norms.version, kbVersion: norms.kbVersion, charts: norms.charts, corpus: norms.corpus },
    radar_note: TAT_ACH_NOTE,
    method: {
      thang: `mỗi lớp là một giá trị thô (bên thuận trừ bên bất lợi), chia cho cỡ thường gặp của chính lớp ấy trên ${norms?.charts ?? 1000} lá số mẫu (không trừ trung bình: lớp không có gì thì góp 0) rồi cộng theo trọng số; năm mức là so với chính loại giai đoạn ấy trên bộ mẫu (các ngưỡng 12 / 33 / 67 / 88 % của những giai đoạn có căn cứ sách; quy ước hệ thống). Lời sách đọc được nghiêng về thuận nhiều hơn (bảng độ sáng có nhiều chỗ đắc hơn hãm), nên “Thuận” nghĩa là thuận hơn các giai đoạn thường gặp; khi mức và chiều lời sách khác nhau, lời văn nói rõ`,
      can_cu: `giai đoạn không có câu sách hay sao nào đã đối chiếu độ sáng để xét thì để mức “${LEVELS[LEVEL_DEFAULT]}” kèm ghi chú “${INSUFFICIENT_VI}”, không phải trung bình thật; tháng không có gì để xét thì “${UNDETERMINED_VI}”`,
      sach_truoc: `lớp có sách quyết định chiều; các lớp thông lệ cộng lại chỉ được thêm tối đa ${vn(CONV_K)} × phần có sách (+ ${vn(CONV_FLOOR)} khi cùng chiều hoặc sách không nói), nên không lật được lời sách. Khi lời sách trái chiều nhau: câu sách về cung vận (một câu = 1; câu có điều kiện hay nhẹ = ½), rồi đắc hãm từng sao (½ câu mỗi sao), Toàn Thư nhập hạn ca ½; lời văn nói rõ bên nào nặng hơn`,
      dai_van: `cung vận ${vn(W_DECADE.van)}: câu sách (Khảo Luận tr.230-236, Thực Hành tr.115-117; Toàn Thư tr.96-106 nhập hạn ca, đã đối chiếu trang, × ${vn(TT_WEIGHT)}), Nam/Bắc đẩu tinh của cung vận (TH tr.115 mục IX.1-2), đắc hãm các chính tinh, trung tinh (KL tr.36), hung tinh của cung vận, xung chiếu, tam hợp và nhị hợp khi nhị hợp sinh cho cung vận (KL tr.233 mục 3-4); Tứ Hóa theo can đại vận ${vn(W_DECADE.hoa_van)} (thông lệ). Mệnh, Thân sáng hay tối chỉ được nói theo các cách của TH tr.118, không cộng trừ điểm`,
      nam: `đại vận đang đi ${vn(W_YEAR.dai_van)}, cung tiểu hạn ${vn(W_YEAR.tieu_han)} (${RULE_VI[inp.rule]}; đọc như cung vận, KL tr.40), cung lưu đại hạn ${vn(W_YEAR.luu_dai_han)} (TH tr.117-118), sao Bắc đẩu của cung đại vận ở năm năm đầu, Nam đẩu ở năm năm sau ${vn(W_YEAR.dau_tinh)} (TH tr.115 mục IX.3-4), lưu Khốc Hư ở tiểu hạn ${vn(W_YEAR.luu_sao)} (TH tr.114); thông lệ: các sao lưu khác ${vn(W_YEAR.luu_sao_tl)} (vị trí KL tr.41-42), lưu Tứ Hóa ${vn(W_YEAR.luu_tu_hoa)} (bỏ khi can năm trùng can đại vận)`,
      thang_am: `mức của năm cộng ${vn(W_MONTH)} × đắc hãm các sao của cung nguyệt hạn và tam phương (vị trí TH tr.115, KL tr.40-41; tiêu chí KL tr.233 mục 4)`,
      ban_menh: `mười hai cung: nhận định đã đối chiếu sách bắn vào cung, cung xung chiếu và hai cung tam hợp; trọng số = tầng × (0,5 + độ hiếm của quy tắc trên chính cung đó) × vị trí (1 / 0,85 / 0,7); so với trung bình của chính cung đó: (tổng + 1) / (trung bình + 1). ${TAT_ACH_NOTE}`,
      bat_tu: 'dải Bát Tự: vận nào mang can hoặc chi thuộc thần điều hậu của bảng Thiệu Vĩ Hoa (tr.389-396); không cộng vào mức Tử Vi',
    },
  };
}
