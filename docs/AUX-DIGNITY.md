# Độ sáng phụ tinh (auxiliary-star dignity) — audit, aux-dignity-1

Data: `engine/data/dignity_aux.json`, built by `tools/build_aux_dignity.py` (the builder holds the transcription, one line per star,
with the page and every misprint noted). Lookup: `tvbt/dignity.py` `minor_dignity_cell` / `minor_dignity`. Tests:
`engine/tests/test_aux_dignity.py` (Python) and `src/interpret/test/dignity.test.ts` (TS parity). Replaces `dignity_minor.json`
(Toàn Thư, 5 stars) and `dignity_aux_th.json` (Thực Hành, 5 stars).

## Method

Every cell was read from the **page image** of Tử Vi Thực Hành (TH), Tử Vi Đẩu Số Toàn Thư (TT) and Tử Vi Khảo Luận (KL),
not from the text layer alone (the TH text layer scrambles lines). Policy:

* Only a branch the book names gets a level. Every other branch is **unknown**: no badge, fact `unspecified`, no rule fires.
* `term` = the word printed; `level` = what rules see. **lợi** (lợi địa) is a level of its own: TH p.64 lists Miếu, Đắc,
  Lợi, Hãm as four tiers. No rule treats it as bright or as hãm. **Exception:** the Văn Xương lợi cells (TH Hợi; TT Tý Thìn Thân
  Hợi Mão Mùi) were already read as đắc in production before this audit. They stay đắc and are marked `legacy` so that no
  production reading changes without a reviewer. **đắc cách** (TH p.51, Tả Hữu) is read as đắc (KL p.121: "đắc địa tứ mộ").
* A cell printed twice with different levels, a label lost to a misprint, or a second-hand quote inside a book goes to
  `experimental`. It is never returned by the lookup.
* Schools are not mixed **inside a star**. The chosen school (`thuc_hanh` default, or `toan_thu`) is used if it tabulates the star
  at all; otherwise the next book in `fallback` (TH → TT → KL, or TT → TH → KL). The badge tooltip names the book and page.

## What each book documents (production cells)

M miếu · V vượng · Đ đắc · Đc đắc cách · L lợi · B bình · H hãm · · = not named (unknown)

| Sao | Sách | Tý | Sửu | Dần | Mão | Thìn | Tỵ | Ngọ | Mùi | Thân | Dậu | Tuất | Hợi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Văn Xương | TH p.50 | Đ | M | H | · | Đ | M | H | · | Đ | M | H | L |
| Văn Xương | TT p.41 | L | M | H | L | L | M | H | L | L | M | H | L |
| Văn Xương | KL p.192 | · | Đ | · | · | Đ | Đ | · | Đ | · | · | Đ | Đ |
| Văn Khúc | TH p.50 | Đ | M | B | V | Đ | M | H | V | Đ | M | H | V |
| Văn Khúc | TT p.43 | M | M | · | V | M | M | H | V | · | M | H | V |
| Văn Khúc | KL p.192 | · | Đ | · | · | Đ | Đ | · | Đ | · | · | Đ | Đ |
| Tả Phụ | TH p.51 | · | Đc | · | · | Đc | · | · | Đc | · | · | Đc | · |
| Tả Phụ | KL p.121 | H | Đ | H | H | Đ | H | H | Đ | H | H | Đ | H |
| Hữu Bật | TH p.51 | · | Đc | · | · | Đc | · | · | Đc | · | · | Đc | · |
| Hữu Bật | KL p.121 | H | Đ | H | H | Đ | H | H | Đ | H | H | Đ | H |
| Thiên Mã | TH p.52 | · | · | Đ | · | · | Đ | · | · | · | · | · | · |
| Long Trì | TH p.54 | · | Đ | · | · | · | · | · | Đ | · | · | · | · |
| Phượng Các | TH p.54 | · | Đ | · | · | · | · | · | Đ | · | · | · | · |
| Kình Dương | TH p.62 | H | Đ | · | H | Đ | · | H | Đ | · | H | Đ | · |
| Kình Dương | TT p.50 | · | M | · | H | M | H | H | M | V | H | M | V |
| Kình Dương | KL p.200 | · | Đ | · | · | Đ | · | · | Đ | · | · | Đ | · |
| Đà La | TH p.63 | · | Đ | H | · | Đ | H | · | Đ | H | · | Đ | H |
| Đà La | TT p.51 | · | M | · | H | M | B | · | M | · | H | M | B |
| Đà La | KL p.200 | · | Đ | · | · | Đ | Đ | · | Đ | · | · | Đ | Đ |
| Hỏa Tinh | TH p.64 | H | Đ | M | L | H | Đ | M | L | H | Đ | M | L |
| Hỏa Tinh | TT p.52 | · | B | M | · | · | B | M | · | · | B | M | H |
| Linh Tinh | TH p.64 | · | H | M | · | · | · | · | · | · | H | M | H |
| Đại Hao | TH p.65 | H | · | Đ | Đ | · | H | H | · | Đ | Đ | · | H |
| Tiểu Hao | TH p.65 | H | · | Đ | Đ | · | H | H | · | Đ | Đ | · | H |
| Tang Môn | TH p.65 | · | · | Đ | Đ | · | · | · | · | Đ | Đ | · | · |
| Bạch Hổ | TH p.65 | · | · | Đ | Đ | · | · | · | · | Đ | Đ | · | · |
| Thiên Khốc | TH p.66 | M | L | · | L | H | · | M | L | · | L | H | · |
| Thiên Khốc | KL p.202 | Đ | · | · | Đ | · | · | Đ | · | · | Đ | · | · |
| Thiên Hư | TH p.66 | M | L | · | L | H | · | M | L | · | L | H | · |
| Thiên Hư | KL p.202 | Đ | · | · | Đ | · | · | Đ | · | · | Đ | · | · |
| Thiên Hình | TH p.67 | · | · | Đ | Đ | · | · | · | · | Đ | Đ | · | · |
| Thiên Hình | KL pp.201-202 | H | H | Đ | Đ | H | H | H | H | Đ | Đ | H | H |
| Địa Không | TH p.67 | · | · | Đ | · | · | Đ | · | · | Đ | · | · | Đ |
| Địa Không | KL p.199 | H | H | Đ | H | H | Đ | H | H | Đ | H | H | Đ |
| Địa Kiếp | TH p.67 | · | · | Đ | · | · | Đ | · | · | Đ | · | · | Đ |
| Địa Kiếp | KL p.199 | H | H | Đ | H | H | Đ | H | H | Đ | H | H | Đ |
| Thiên Riêu | TH p.68 | · | · | Đ | Đ | · | · | · | · | · | Đ | Đ | · |
| Thiên Riêu | KL p.121 | · | · | · | Đ | · | · | · | · | · | Đ | · | · |
| Lộc Tồn | TT p.47 | M | M | M | M | M | M | M | M | M | M | M | M |
| Kiếp Sát | KL p.201 | · | · | Đ | · | · | Đ | · | · | Đ | · | · | Đ |
| Thiên Không | KL p.147 | · | · | Đ | · | · | Đ | · | · | Đ | · | · | Đ |

Which book is actually shown: TH school = TH for its 21 stars, TT for **Lộc Tồn**, KL for **Kiếp Sát** and **Thiên Không**.
TT school = TT for its 6 stars, then TH, then KL. KL is otherwise reference only.

## No classification in any book (kept unknown)

Thiên Khôi, Thiên Việt (TT p.46: "không thấy nói tới hãm địa"), Đào Hoa, Hồng Loan, Thiên Hỷ, Ân Quang, Thiên Quý, Tam Thai,
Bát Tọa, Hoa Cái, Thiên Quan, Thiên Phúc, Thiên Y, Cô Thần, Quả Tú, Đẩu Quân, Phá Toái, Lưu Hà, Thiên Thương, Thiên Sứ,
Thiên/Nguyệt Đức, Thiên/Địa Giải, Thiên La, Địa Võng, Thiên Tài, Thiên Thọ, and the Lộc Tồn / Thái Tuế / Trường Sinh rings apart
from Đại Hao, Tiểu Hao, Tang Môn, Bạch Hổ. Full list with page notes: `no_table` in the JSON.

## Disputed / experimental (not in production)

| Sao | Sách | Cells | Why |
|---|---|---|---|
| Kình Dương | TT p.50 | Tý | First phú says vượng, the fourth says "bốn cung hãm Tí, Ngọ, Mão, Dậu". Same treatment the engine already gives Tham Lang Tý in TT. |
| Linh Tinh | TH p.64 | Thìn, Mùi, Tỵ | "Miếu: Dần, Tuất – Thìn, Tỵ, Mùi" (label after the dash missing) and Tỵ also under Hãm. |
| Văn Xương | TT p.41 | Thìn, Tỵ, Ngọ, Mão, Dậu | The song contradicts the phú list. TT p.42 says it cannot be settled; production keeps the phú list. |
| Văn Khúc | TT p.43 | Tý, Hợi | Song "Lạc cư Hợi, Tí cung" vs phú (Tý miếu, Hợi vượng). |
| Hỏa Tinh | TT p.52 | Tý, Mão miếu | Reported Vietnamese variant. |
| Thiên Khốc/Hư | TT p.57 | Tý Ngọ vs Mão Dậu Thân | TT records two schools (VN phú vs La Hồng Tiên/Hi Di). |
| Bạch Hổ, Hồng Loan, Long Trì/Phượng Các | TT pp.60-62 | — | Second-hand ("Tử Vi Việt", phú nôm). |
| Ân Quang/Thiên Quý | TH p.55 | Sửu, Mùi | Prose about a cách, not a brightness header. |
| Đà La | KL p.143 | Tứ chính | Reported "có sách nói" variant, argued against by KL. |
| Tứ Hóa | TH pp.52-53, TT pp.48-50 | — | Transformations, not Thiên Bàn stars. Hóa Kỵ tứ mộ is vượng (header) vs đắc (prose) in TH. TT gives Quyền "Dần Mão Tỵ Hợi". |

## Where the books disagree on a named cell (school variants, both kept)

Strong inversions (good vs hãm):
* **Đà La Tỵ/Hợi**: TH hãm · TT bình · KL đắc.
* **Hỏa Tinh Hợi**: TH lợi · TT hãm.
* **Văn Xương/Khúc Tuất**: TH, TT hãm · KL đắc (tứ mộ).
* **Kình Dương Tý**: TH hãm · TT disputed.

Tier differences only: Kình/Đà tứ mộ (TH, KL đắc vs TT miếu), Hỏa Tỵ Dậu Sửu (TH đắc vs TT bình), Văn Khúc Tý/Thìn
(TH đắc vs TT miếu), Bạch Hổ Dậu (TH đắc vs TT-quoted miếu).

## Effect on production (A/B over 120 births, HEAD vs this change, /api/reasoning tu_vi findings)

| School | Charts changed | Findings + / − | Cause (every one traced to a cell above) |
|---|---|---|---|
| thuc_hanh (default) | 22/120 | +15 / −12 | Kình Tý now TH hãm (was TT vượng by fallback): −9 bright, +5 hãm findings. Hỏa Tỵ now TH đắc: +5. Linh Tinh now has levels: +5 (3 rules that could never fire). Kình tứ mộ now TH đắc instead of TT miếu: −2 `TV_TT_MENH_KINH_MIEU`. |
| toan_thu | 15/120 | +5 / −10 | Kình Tý disputed → unknown: −10. Linh Tinh via TH fallback: +5. |

**Open question for a reviewer:** `TV_TT_MENH_KINH_MIEU` ("Kình Dương nhập miếu", TT p.50) requires exactly `miếu`. In the TH
school, TH labels the same tứ mộ cells `đắc`, so this TT rule no longer fires there. Both books agree tứ mộ is Kình's good seat; only
the tier label differs. The rule is unchanged. Widening its gate to `[miếu, đắc]` would restore it, but that is a rule edit and needs
review. The other open point is the `lợi` reading for Văn Xương (`legacy`).

## UI

The palace cell and the palace drawer show the existing compact badge next to each phụ tinh that has a known level. The badge prints
the book's term (Lợi, Đắc for đắc cách). The tooltip gives the level used, the book and the page. A star with an unknown level gets no
badge. The glossary has a new "Lợi" entry.
