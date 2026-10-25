# Plan (b): result (2026-10-25)

Plan: [PLAN-B-MINING-2026-10-25.md](PLAN-B-MINING-2026-10-25.md). Mined Khảo Luận (KL), Thực Hành (TH) and Toàn Thư (TT) for seven thin palaces.

## What was mined

| Book | Lines | Phu Thê | Điền Trạch | Tử Tức | Nô Bộc | Phụ Mẫu | Tật Ách | Huynh Đệ |
|---|---|---|---|---|---|---|---|---|
| KL | 47 | 21 | 17 | 1 | 2 | 0 | 5 | 1 |
| TH | 76 | 32 | 14 | 16 | 1 | 3 | 6 | 4 |
| TT | 101 | 22 | 32 | 4 | 19 | 10 | 8 | 6 |

- Every line has its printed page and a verbatim quote. `engine/tests/test_planb.py` finds each quote on its page.
- TH lines were read on the page image, because TH's text layer scrambles line order.
- Conditions follow the book's own conditions and are never widened.
- These were left out on purpose:
  - appearance and illness names;
  - any health verdict (Tật Ách keeps only what the stars do there);
  - death, khắc, prison and theft;
  - events and hạn lines.

## Checked before becoming rules (`tools/interpret/planb_overlap.py`)

- **33 duplicates**: an existing verified rule already says the same thing on the same conditions. These lines are left out of the pack and listed in `quotes_planb.json` under `duplicates`.
- **2 contradictions** are kept, and the KG records each as two books that disagree:
  - TT p.49: Hóa Kỵ at Điền Trạch is "đắc dụng". Hàm Số says it loses the house.
  - TT p.34: Cự Môn at Điền Trạch "dễ phá tổ nghiệp". KL reads it differently.
- **12 same-conditions entries**: they say something else about a placement that already has a rule. They are kept.
- **Dropped by hand**: TT_NO_BOC_TU_VI_SAI_CHO. On a borrowed Tử Vi it produced "Tử Vi ở Nô Bộc là ngồi sai chỗ", which contradicts TT's own nearby line.
- **Fixed in passing**:
  - TH p.59, Điền Trạch and Tài Bạch: the line sits under "8>TỬ", not Mộ (checked on the page image). The rules were corrected.
  - A Hàm Số card had a doubled `{S}`.

The result is `engine/data/pack_planb.json` with 191 rules.

## Depth (150 charts, median, before → after)

| Palace | Book sentences | Main reading | Distinct rules told |
|---|---|---|---|
| Tử Tức | 7→8 | 2→3 | 4→6 |
| Điền Trạch | 8→8 | 3→4 | 5→7 |
| Phu Thê | 7→7 | 3→4 | 5→6 |
| Phụ Mẫu | 7→8 | 3→3 | 6→7 |
| Nô Bộc | 9→9 | 3→3 | 7→7 |
| Tật Ách | 5→5 | 2→2 | 3→3 |
| Huynh Đệ | 5→5 | 2→2 | 4→4 |

- Huynh Đệ and Tật Ách stay flat. The three books say little there that is not a duplicate, an illness name or an event.
- Readability stays inside its gates: strip 0.061 (gate 0.0655) and Barnum 39.5%.
- Goldens were regenerated only after reading their diffs.
- The synthesis metamorphic test was narrowed for one reason. The clean Phu Thê variant now carries a legitimate Cô Quả strain (KL p.153). With no limit present, no strain may rest on a limit, but that strain is allowed to stay.
